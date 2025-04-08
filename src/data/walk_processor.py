"""
Process walking data from various sources.
"""
import xml.etree.ElementTree as ET
import geopandas as gpd
from shapely.geometry import LineString, Point
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pytz
from ..utils.config import DEFAULT_CRS, MIN_WALK_DURATION, MIN_WALK_DISTANCE, METRIC_CRS

def parse_tcx_file(file_path: str) -> Optional[Dict]:
    """Parse a TCX file and extract walk data."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # TCX files use a namespace
        ns = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
        
        # Get activity type
        activity = root.find('.//ns:Activity', ns)
        if activity is None:
            return None
            
        activity_type = activity.get('Sport')
        if activity_type != 'Walking':
            return None
            
        # Get trackpoints
        trackpoints = []
        for trackpoint in root.findall('.//ns:Trackpoint', ns):
            time = trackpoint.find('ns:Time', ns)
            position = trackpoint.find('ns:Position', ns)
            
            if time is not None and position is not None:
                lat = position.find('ns:LatitudeDegrees', ns)
                lon = position.find('ns:LongitudeDegrees', ns)
                
                if lat is not None and lon is not None:
                    trackpoints.append({
                        'time': datetime.fromisoformat(time.text.replace('Z', '+00:00')),
                        'lat': float(lat.text),
                        'lon': float(lon.text)
                    })
        
        if len(trackpoints) < 2:
            return None
            
        # Create walk data
        coords = [(tp['lon'], tp['lat']) for tp in trackpoints]
        times = [tp['time'] for tp in trackpoints]
        
        return {
            'geometry': LineString(coords),
            'start_time': times[0],
            'end_time': times[-1],
            'source_file': Path(file_path).name
        }
        
    except Exception as e:
        print(f"Error parsing TCX file {file_path}: {e}")
        return None

def process_walk_files(directory: str) -> gpd.GeoDataFrame:
    """Process all walk files in a directory."""
    walks = []
    tcx_files = list(Path(directory).glob('*.tcx'))
    
    print(f"Found {len(tcx_files)} TCX files")
    
    for file_path in tcx_files:
        walk_data = parse_tcx_file(str(file_path))
        if walk_data is not None:
            # Calculate duration
            duration = (walk_data['end_time'] - walk_data['start_time']).total_seconds()
            
            # Create a temporary GeoDataFrame to calculate distance in meters
            temp_gdf = gpd.GeoDataFrame(geometry=[walk_data['geometry']], crs=DEFAULT_CRS)
            temp_gdf = temp_gdf.to_crs(METRIC_CRS)
            distance = temp_gdf.geometry.iloc[0].length
            
            # Filter out walks that are too short
            if duration >= MIN_WALK_DURATION and distance >= MIN_WALK_DISTANCE:
                walks.append(walk_data)
    
    if not walks:
        return gpd.GeoDataFrame()
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(walks, crs=DEFAULT_CRS)
    
    print(f"Processed {len(gdf)} valid walks")
    return gdf

def analyze_walks(walks_gdf: gpd.GeoDataFrame, streets_gdf: gpd.GeoDataFrame) -> Dict:
    """Analyze walks and calculate street coverage using optimized spatial operations."""
    from ..utils.config import CITY_PARAMS
    
    city = 'new_york'
    params = CITY_PARAMS[city]
    
    # Filter out transit trips from walks
    valid_walks = []
    for _, walk in walks_gdf.iterrows():
        # Calculate metrics
        coords = list(walk.geometry.coords)
        duration = (walk.end_time - walk.start_time).total_seconds()
        
        # Calculate distance
        temp_gdf = gpd.GeoDataFrame(geometry=[walk.geometry], crs=walks_gdf.crs)
        temp_gdf = temp_gdf.to_crs(METRIC_CRS)
        distance = temp_gdf.geometry.iloc[0].length
        
        # Calculate average speed (m/s)
        avg_speed = distance / duration if duration > 0 else 0
        
        # Calculate sinuosity (path straightness)
        start_point = Point(coords[0])
        end_point = Point(coords[-1])
        straight_distance = start_point.distance(end_point)
        sinuosity = distance / straight_distance if straight_distance > 0 else 1
        
        # Only include clear walking segments:
        # 1. Speed within walking range
        # 2. Natural path sinuosity
        # 3. Reasonable walking distance
        if (avg_speed <= params['max_walking_speed'] * 1.2 and  # Allow 20% buffer
            avg_speed >= params['min_walking_speed'] and  # Minimum walking speed
            (sinuosity >= 1.05 or distance <= 2000) and  # Allow straight paths only for short distances
            distance <= 5000):  # Maximum realistic walking distance of 5 km
            valid_walks.append(walk)
    
    valid_walks_gdf = gpd.GeoDataFrame(valid_walks, crs=walks_gdf.crs)
    print(f"Found {len(valid_walks_gdf)} valid walks out of {len(walks_gdf)} total walks")
    
    # Create a copy of streets for results
    streets_gdf = streets_gdf.copy()
    streets_gdf['covered'] = False
    streets_gdf['coverage_percent'] = 0.0
    streets_gdf['covered_segments'] = None  # To store individual covered segments
    
    # Convert to metric CRS for accurate buffering and distance calculations
    valid_walks_gdf = valid_walks_gdf.to_crs(METRIC_CRS)
    streets_gdf = streets_gdf.to_crs(METRIC_CRS)
    
    # Create spatial index for streets
    streets_sindex = streets_gdf.sindex
    
    # Buffer all walks at once and create spatial index for walks
    buffered_walks = valid_walks_gdf.copy()
    buffered_walks['geometry'] = buffered_walks.geometry.buffer(params['buffer_distance'])
    walks_sindex = buffered_walks.sindex
    
    # Process streets in larger batches for better performance
    batch_size = 5000
    covered_streets = []
    
    for i in range(0, len(streets_gdf), batch_size):
        batch_streets = streets_gdf.iloc[i:i+batch_size]
        
        # Find all potentially intersecting walks for the entire batch
        batch_bounds = batch_streets.geometry.bounds
        possible_matches_idx = set()
        for _, bounds in batch_bounds.iterrows():
            # Convert bounds to tuple format (minx, miny, maxx, maxy)
            bounds_tuple = (bounds.minx, bounds.miny, bounds.maxx, bounds.maxy)
            matches = list(walks_sindex.intersection(bounds_tuple))
            possible_matches_idx.update(matches)
        
        if not possible_matches_idx:
            continue
            
        # Get the actual intersecting walks for the batch
        relevant_walks = buffered_walks.iloc[list(possible_matches_idx)]
        
        # Process each street in the batch
        for idx, street in batch_streets.iterrows():
            # Find walks that intersect with this street
            intersecting_walks = relevant_walks[relevant_walks.intersects(street.geometry)]
            
            if not intersecting_walks.empty:
                # Calculate intersections and filter out potential transit segments
                covered_segments = []
                total_covered_length = 0
                
                for _, walk in intersecting_walks.iterrows():
                    intersection = street.geometry.intersection(walk.geometry)
                    if not intersection.is_empty:
                        # For each covered segment, check if it's likely a transit segment
                        if hasattr(intersection, 'geoms'):
                            # Multiple segments
                            for segment in intersection.geoms:
                                if segment.length > 0:
                                    segment_length = segment.length
                                    # Only include segments that are likely walking
                                    if segment_length <= 500:  # Max 500m per segment
                                        covered_segments.append(segment)
                                        total_covered_length += segment_length
                        else:
                            # Single segment
                            segment_length = intersection.length
                            if segment_length > 0 and segment_length <= 500:
                                covered_segments.append(intersection)
                                total_covered_length += segment_length
                
                if covered_segments:
                    # Calculate coverage percentage
                    if street.geometry.length > 0:
                        coverage_percent = (total_covered_length / street.geometry.length) * 100
                        if coverage_percent > 0:
                            street_data = street.copy()
                            street_data['coverage_percent'] = min(coverage_percent, 100)
                            street_data['covered'] = True
                            covered_streets.append(street_data)
    
    # Create final GeoDataFrame with only covered streets
    if covered_streets:
        result_streets = gpd.GeoDataFrame(covered_streets, crs=METRIC_CRS)
    else:
        result_streets = gpd.GeoDataFrame(geometry=[], crs=METRIC_CRS)
    
    # Convert back to original CRS
    result_streets = result_streets.to_crs(walks_gdf.crs)
    valid_walks_gdf = valid_walks_gdf.to_crs(walks_gdf.crs)
    
    return result_streets, valid_walks_gdf 