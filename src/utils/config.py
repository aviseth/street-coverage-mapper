"""
Configuration settings for street coverage mapping.
"""
import logging
from pathlib import Path

# Legacy city parameters for backwards compatibility
LEGACY_CITY_PARAMS = {
    'new_york': {
        'buffer_distance': 5,  # meters
        'max_walking_speed': 3.0,  # m/s (10.8 km/h)
        'min_walking_speed': 0.1,  # m/s (0.36 km/h)
        'max_sinuosity': 4.0,
        'max_direct_distance': 15000,  # meters (15 km)
        'bbox': [-74.3, 40.5, -73.7, 40.9],  # [min_lon, min_lat, max_lon, max_lat]
    },
    'london': {
        'buffer_distance': 8,  # meters - increased for better GPS handling
        'max_walking_speed': 3.0,  # m/s (10.8 km/h)
        'min_walking_speed': 0.1,  # m/s (0.36 km/h)
        'max_sinuosity': 4.0,
        'max_direct_distance': 15000,  # meters (15 km)
        'bbox': [-0.6, 51.1, 0.4, 51.8],  # [min_lon, min_lat, max_lon, max_lat]
        'boroughs': [
            "City of London",
            "Westminster",
            "Kensington and Chelsea",
            "Hammersmith and Fulham",
            "Wandsworth",
            "Lambeth",
            "Southwark",
            "Tower Hamlets",
            "Hackney",
            "Islington",
            "Camden",
            "Brent",
            "Ealing",
            "Hounslow",
            "Richmond upon Thames",
            "Kingston upon Thames",
            "Merton",
            "Sutton",
            "Croydon",
            "Bromley",
            "Lewisham",
            "Greenwich",
            "Bexley",
            "Havering",
            "Barking and Dagenham",
            "Redbridge",
            "Newham",
            "Waltham Forest",
            "Haringey",
            "Enfield",
            "Barnet",
            "Harrow",
            "Hillingdon"
        ]
    }
}

def get_city_parameters(city_name: str):
    """
    Get parameters for any city, using auto-detection or legacy configs.
    
    Args:
        city_name: Name of the city (can be any city worldwide)
        
    Returns:
        Dict containing optimized parameters for the city
    """
    # Check if it's a legacy city with predefined parameters
    if city_name.lower() in LEGACY_CITY_PARAMS:
        logging.info(f"Using legacy parameters for {city_name}")
        return LEGACY_CITY_PARAMS[city_name.lower()]
    
    # Use auto-detection for new cities
    try:
        from .city_analyzer import get_city_parameters as analyze_city
        cache_dir = str(Path(PROCESSED_DATA_DIR) / 'city_cache')
        return analyze_city(city_name, cache_dir)
    except ImportError:
        logging.error("City analyzer not available, falling back to default parameters")
        return get_default_parameters()

def get_default_parameters():
    """Get default parameters for unknown cities."""
    return {
        'buffer_distance': 8,
        'max_walking_speed': 3.0,
        'min_walking_speed': 0.1,
        'max_sinuosity': 4.0,
        'max_direct_distance': 15000,
        'bbox': None
    }

# For backwards compatibility
CITY_PARAMS = LEGACY_CITY_PARAMS

# File paths
DATA_DIR = 'data'
RAW_DATA_DIR = f'{DATA_DIR}/raw'
PROCESSED_DATA_DIR = f'{DATA_DIR}/processed'

# CRS settings
DEFAULT_CRS = 'EPSG:4326'
METRIC_CRS = 'EPSG:3857'   # Web Mercator

# Analysis settings
MIN_WALK_DURATION = 0  # seconds
MIN_WALK_DISTANCE = 0  # meters
GPS_ACCURACY = 15  # meters - increased for urban environments 