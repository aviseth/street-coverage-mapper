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
    """Analyze walks and calculate street coverage."""
    from ..utils.config import CITY_PARAMS
    
    city = 'new_york'
    params = CITY_PARAMS[city]
    
    # Filter out transit trips
    valid_walks = []
    for _, walk in walks_gdf.iterrows():
        # Calculate metrics
        coords = list(walk.geometry.coords)
        duration = (walk.end_time - walk.start_time).total_seconds()
        
        # Calculate distance
        temp_gdf = gpd.GeoDataFrame(geometry=[walk.geometry], crs=walks_gdf.crs)
        temp_gdf = temp_gdf.to_crs(METRIC_CRS)
        distance = temp_gdf.geometry.iloc[0].length
        
        # Calculate average speed
        avg_speed = distance / duration if duration > 0 else 0
        
        # Calculate sinuosity (path straightness)
        start_point = Point(coords[0])
        end_point = Point(coords[-1])
        straight_distance = start_point.distance(end_point)
        sinuosity = distance / straight_distance if straight_distance > 0 else 1
        
        # Only filter out clear transit cases:
        # 1. Speed significantly above walking speed (with buffer)
        # 2. Very straight paths (sinuosity < 1.05) for longer distances
        # 3. Paths longer than 5 km (likely transit)
        if (avg_speed <= params['max_walking_speed'] * 1.2 and  # Allow 20% buffer
            not (distance > 2000 and sinuosity < 1.05) and  # Only filter very straight long paths
            distance <= 5000):  # Maximum realistic walking distance of 5 km
            valid_walks.append(walk)
    
    valid_walks_gdf = gpd.GeoDataFrame(valid_walks, crs=walks_gdf.crs)
    print(f"Found {len(valid_walks_gdf)} valid walks out of {len(walks_gdf)} total walks")
    
    # Calculate street coverage
    streets_gdf = streets_gdf.copy()
    streets_gdf['covered'] = False
    streets_gdf['coverage_percent'] = 0.0
    
    for idx, street in streets_gdf.iterrows():
        street_geom = street.geometry
        covered_length = 0
        
        for _, walk in valid_walks_gdf.iterrows():
            walk_geom = walk.geometry
            buffered_walk = walk_geom.buffer(params['buffer_distance'])
            
            # Calculate intersection length
            intersection = street_geom.intersection(buffered_walk)
            if not intersection.is_empty:
                covered_length += intersection.length
        
        # Calculate coverage percentage
        if street_geom.length > 0:
            coverage_percent = (covered_length / street_geom.length) * 100
            streets_gdf.loc[idx, 'coverage_percent'] = min(coverage_percent, 100)
            streets_gdf.loc[idx, 'covered'] = coverage_percent > 0
    
    return streets_gdf, valid_walks_gdf 