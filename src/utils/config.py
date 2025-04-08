"""
Configuration settings for street coverage mapping.
"""

# City parameters
CITY_PARAMS = {
    'new_york': {
        'buffer_distance': 8,  # meters
        'max_walking_speed': 2.5,  # m/s
        'min_walking_speed': 0.2,  # m/s
        'max_sinuosity': 3.0,  # for longer trips
        'max_direct_distance': 10000,  # meters
        'bbox': [-74.3, 40.5, -73.7, 40.9],  # [min_lon, min_lat, max_lon, max_lat]
    }
}

# File paths
DATA_DIR = 'data'
RAW_DATA_DIR = f'{DATA_DIR}/raw'
PROCESSED_DATA_DIR = f'{DATA_DIR}/processed'

# CRS settings
DEFAULT_CRS = 'EPSG:4326'  # WGS84
METRIC_CRS = 'EPSG:3857'   # Web Mercator

# Analysis settings
MIN_WALK_DURATION = 60  # seconds
MIN_WALK_DISTANCE = 100  # meters
GPS_ACCURACY = 10  # meters 