"""
Configuration settings for street coverage mapping.
"""

# City parameters
CITY_PARAMS = {
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