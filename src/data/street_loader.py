"""
Load and process street network data.
"""
import os
import geopandas as gpd
import osmnx as ox
from ..utils.config import PROCESSED_DATA_DIR, DEFAULT_CRS, CITY_PARAMS
import pandas as pd

def load_street_network(city: str = 'new_york'):
    """Load or download street network for the specified city."""
    if city not in CITY_PARAMS:
        raise ValueError(f"Unsupported city: {city}. Must be one of {list(CITY_PARAMS.keys())}")
    
    params = CITY_PARAMS[city]
    cache_file = os.path.join(PROCESSED_DATA_DIR, f"{city}_streets.geojson")
    
    # Check if we have a cached version
    if os.path.exists(cache_file):
        print(f"Loading streets from cache: {cache_file}")
        return gpd.read_file(cache_file)
    
    print(f"Downloading street network for {city}...")
    
    if city == 'new_york':
        # Define areas to load for NYC
        areas = [
            "Manhattan, New York, USA",
            "Brooklyn, New York, USA",
            "Queens, New York, USA",
            "Staten Island, New York, USA",
            "Bronx, New York, USA",
            "Jersey City, New Jersey, USA",
            "Hoboken, New Jersey, USA"
        ]
    else:  # London
        # Use boroughs from config
        areas = [f"{borough}, London, UK" for borough in params['boroughs']]
    
    all_streets = []
    
    for area in areas:
        print(f"Loading streets for {area}...")
        try:
            # Download street network
            G = ox.graph_from_place(area, network_type='drive')
            
            # Convert to GeoDataFrame
            streets_gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
            all_streets.append(streets_gdf)
        except Exception as e:
            print(f"Error loading streets for {area}: {e}")
    
    if not all_streets:
        print("No street networks could be loaded")
        return gpd.GeoDataFrame(geometry=[], crs=DEFAULT_CRS)
    
    # Combine all street networks
    streets_gdf = gpd.GeoDataFrame(pd.concat(all_streets, ignore_index=True))
    
    # Create a unique ID for each street segment
    streets_gdf['street_id'] = streets_gdf.index
    
    # Initialize coverage columns
    streets_gdf['covered'] = False
    streets_gdf['coverage_percent'] = 0.0
    
    # Save to file
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    streets_gdf.to_file(cache_file, driver='GeoJSON')
    
    return streets_gdf 