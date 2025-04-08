#!/usr/bin/env python3
"""
Process TCX files from Google Fit to extract street coverage data.
"""

import os
import xml.etree.ElementTree as ET
import geopandas as gpd
from shapely.geometry import LineString, Point
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('processing.log')
    ]
)

# TCX namespace
TCX_NS = {
    'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
}

def safe_extract_text(element, xpath, namespaces):
    """Safely extract text from an XML element."""
    if element is None:
        return None
    found = element.find(xpath, namespaces)
    return found.text if found is not None else None

def add_style_properties(gdf, style_type):
    """Add style properties to the GeoDataFrame for Kepler.gl visualization."""
    if style_type == 'walk':
        gdf['stroke'] = '#3182CE'  # Blue color
        gdf['stroke-width'] = 2
        gdf['stroke-opacity'] = 0.8
        gdf['stroke-dasharray'] = ''  # Empty string for solid line
    elif style_type == 'street':
        gdf['stroke'] = '#E53E3E'  # Red color for covered streets
        gdf['stroke-width'] = 3
        gdf['stroke-opacity'] = 0.8
        gdf['stroke-dasharray'] = ''
    return gdf

def parse_tcx_file(tcx_file):
    """Parse a TCX file and extract GPS coordinates and timestamps."""
    try:
        tree = ET.parse(tcx_file)
        root = tree.getroot()
        
        # Find all trackpoints
        trackpoints = root.findall('.//ns:Trackpoint', TCX_NS)
        logging.info(f"Found {len(trackpoints)} trackpoints in {tcx_file}")
        
        data = []
        skipped_points = 0
        
        for tp in trackpoints:
            try:
                # Get time
                time = safe_extract_text(tp, 'ns:Time', TCX_NS)
                if time is None:
                    skipped_points += 1
                    continue
                
                # Validate timestamp format
                try:
                    timestamp = datetime.fromisoformat(time.replace('Z', '+00:00'))
                except ValueError:
                    logging.warning(f"Invalid timestamp format in {tcx_file}: {time}")
                    skipped_points += 1
                    continue
                
                # Get position
                position = tp.find('ns:Position', TCX_NS)
                if position is None:
                    skipped_points += 1
                    continue
                
                lat_text = safe_extract_text(position, 'ns:LatitudeDegrees', TCX_NS)
                lon_text = safe_extract_text(position, 'ns:LongitudeDegrees', TCX_NS)
                
                if lat_text is None or lon_text is None:
                    skipped_points += 1
                    continue
                
                try:
                    lat = float(lat_text)
                    lon = float(lon_text)
                    
                    # Basic coordinate validation
                    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                        logging.warning(f"Invalid coordinates in {tcx_file}: lat={lat}, lon={lon}")
                        skipped_points += 1
                        continue
                        
                    data.append({
                        'timestamp': timestamp,
                        'latitude': lat,
                        'longitude': lon
                    })
                except ValueError as e:
                    logging.warning(f"Error converting coordinates in {tcx_file}: {str(e)}")
                    skipped_points += 1
                    continue
                    
            except Exception as e:
                logging.warning(f"Error parsing trackpoint in {tcx_file}: {str(e)}")
                skipped_points += 1
                continue
        
        if skipped_points > 0:
            logging.warning(f"Skipped {skipped_points} invalid trackpoints in {tcx_file}")
        
        if not data:
            logging.warning(f"No valid trackpoints found in {tcx_file}")
            return None
            
        # Create LineString from points
        coords = [(d['longitude'], d['latitude']) for d in data]
        if len(coords) < 2:
            logging.warning(f"Not enough valid points to create LineString in {tcx_file}")
            return None
            
        return {
            'geometry': LineString(coords),
            'start_time': data[0]['timestamp'],
            'end_time': data[-1]['timestamp'],
            'source_file': Path(tcx_file).name
        }
        
    except ET.ParseError as e:
        logging.error(f"XML parsing error in {tcx_file}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error processing {tcx_file}: {str(e)}")
        return None

def analyze_street_coverage(walks_gdf, streets_gdf):
    """Analyze which streets have been covered by the walks."""
    # Buffer the walks slightly to ensure we catch streets that were walked on
    buffered_walks = walks_gdf.copy()
    buffered_walks['geometry'] = buffered_walks['geometry'].buffer(0.0001)  # ~11 meters
    
    # Find intersections between walks and streets
    covered_streets = streets_gdf.copy()
    covered_streets['covered'] = False
    
    for _, walk in buffered_walks.iterrows():
        # Find streets that intersect with this walk
        intersections = streets_gdf[streets_gdf.intersects(walk['geometry'])]
        covered_streets.loc[intersections.index, 'covered'] = True
    
    # Add coverage statistics
    total_streets = len(covered_streets)
    covered_count = covered_streets['covered'].sum()
    coverage_percentage = (covered_count / total_streets) * 100
    
    logging.info(f"Street coverage analysis:")
    logging.info(f"Total streets: {total_streets}")
    logging.info(f"Covered streets: {covered_count}")
    logging.info(f"Coverage percentage: {coverage_percentage:.2f}%")
    
    return covered_streets

def is_probable_transit(walk_data):
    """Determine if a path is likely a transit trip."""
    if walk_data is None:
        return True
        
    # Calculate metrics
    coords = list(walk_data['geometry'].coords)
    duration = (walk_data['end_time'] - walk_data['start_time']).total_seconds()
    
    # Calculate distance
    temp_gdf = gpd.GeoDataFrame(geometry=[walk_data['geometry']], crs='EPSG:4326')
    temp_gdf = temp_gdf.to_crs('EPSG:3857')  # Convert to metric CRS for accurate distance
    distance = temp_gdf.geometry.iloc[0].length / 1000  # Convert to kilometers
    
    # Calculate average speed
    avg_speed = distance / (duration / 3600) if duration > 0 else 0  # km/h
    
    # Calculate sinuosity (ratio of actual path length to straight-line distance)
    start_point = Point(coords[0])
    end_point = Point(coords[-1])
    straight_distance = start_point.distance(end_point) / 1000  # Convert to kilometers
    sinuosity = distance / straight_distance if straight_distance > 0 else 1
    
    # Calculate point density (points per km)
    point_density = len(coords) / distance if distance > 0 else 0
    
    # Transit detection criteria
    MAX_WALKING_SPEED = 7  # km/h
    MIN_POINT_DENSITY = 50  # points per km
    MIN_SINUOSITY = 1.05  # Almost straight line indicates transit
    MIN_STREET_FOLLOWING = 0.3  # Minimum percentage of route that should follow streets
    
    # First check basic transit indicators
    is_transit = (
        avg_speed > MAX_WALKING_SPEED or
        (sinuosity < MIN_SINUOSITY and 
         distance > 0.5 and  # Only check sinuosity for longer segments
         point_density < MIN_POINT_DENSITY)  # Low point density suggests GPS interpolation
    )
    
    # Only check street-following for straight routes
    if not is_transit and sinuosity < MIN_SINUOSITY and distance > 0.5:
        # Load street network
        streets_gdf = gpd.read_file('data/raw/nyc_streets.geojson')
        streets_gdf.set_crs(epsg=4326, inplace=True)
        
        # Buffer the walk line slightly to catch nearby streets
        buffered_walk = walk_data['geometry'].buffer(0.0001)  # ~11 meters
        
        # Find streets that intersect with the buffered walk
        intersecting_streets = streets_gdf[streets_gdf.intersects(buffered_walk)]
        
        # Calculate the percentage of the walk that follows streets
        if not intersecting_streets.empty:
            # Create a union of all intersecting streets
            street_union = intersecting_streets.unary_union
            # Calculate the length of the walk that follows streets
            street_following_length = walk_data['geometry'].intersection(street_union).length
            # Calculate the percentage of the walk that follows streets
            street_following_percentage = street_following_length / walk_data['geometry'].length
        else:
            street_following_percentage = 0
        
        # If the route is straight but doesn't follow streets, it's likely transit
        if street_following_percentage < MIN_STREET_FOLLOWING:
            is_transit = True
    
    if is_transit:
        logging.info(
            f"Skipping transit activity: "
            f"avg_speed={avg_speed:.2f} km/h, "
            f"distance={distance:.2f} km, "
            f"sinuosity={sinuosity:.2f}, "
            f"point_density={point_density:.1f} points/km"
            + (f", street_following={street_following_percentage:.1%}" if 'street_following_percentage' in locals() else "")
        )
    
    return is_transit

def process_tcx_files(input_dir, output_dir):
    """Process all TCX files in the input directory and save as GeoJSON."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    tcx_files = list(input_path.glob('*.tcx'))
    if not tcx_files:
        logging.error(f"No TCX files found in {input_dir}")
        return
        
    logging.info(f"Found {len(tcx_files)} TCX files to process")
    
    walks = []
    for tcx_file in tcx_files:
        logging.info(f"Processing {tcx_file.name}")
        walk_data = parse_tcx_file(tcx_file)
        if walk_data is not None and not is_probable_transit(walk_data):
            walks.append(walk_data)
    
    if walks:
        # Create GeoDataFrame with walks
        walks_gdf = gpd.GeoDataFrame(walks)
        walks_gdf.set_crs(epsg=4326, inplace=True)  # Set WGS84 CRS
        
        # Add style properties for Kepler.gl
        walks_gdf['data_type'] = 'walk'
        walks_gdf = add_style_properties(walks_gdf, 'walk')
        
        # Load street network
        streets_gdf = gpd.read_file('data/raw/nyc_streets.geojson')
        streets_gdf.set_crs(epsg=4326, inplace=True)
        
        # Analyze street coverage
        covered_streets = analyze_street_coverage(walks_gdf, streets_gdf)
        
        # Filter to only covered streets
        covered_streets = covered_streets[covered_streets['covered']]
        
        # Add style properties for covered streets
        covered_streets['data_type'] = 'street'
        covered_streets = add_style_properties(covered_streets, 'street')
        
        # Save results
        walks_gdf.to_file(output_path / 'walks.geojson', driver='GeoJSON')
        covered_streets.to_file(output_path / 'covered_streets.geojson', driver='GeoJSON')
        
        logging.info(f"Processed {len(walks)} valid walks")
        logging.info(f"Found {len(covered_streets)} covered streets")
    else:
        logging.warning("No valid walks found to process")

if __name__ == "__main__":
    input_dir = "data/raw"
    output_dir = "data/processed"
    process_tcx_files(input_dir, output_dir) 