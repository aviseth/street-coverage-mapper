"""
Load and process street network data.
"""
import os
import geopandas as gpd
import osmnx as ox
from ..utils.config import PROCESSED_DATA_DIR, DEFAULT_CRS, get_city_parameters, LEGACY_CITY_PARAMS
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_street_network(city: str):
    """Load or download street network for any city worldwide."""
    # Clean city name for caching
    clean_name = city.lower().replace(' ', '_').replace(',', '').replace('/', '_')
    cache_file = os.path.join(PROCESSED_DATA_DIR, f"{clean_name}_streets.geojson")
    
    # Check if we have a cached version
    if os.path.exists(cache_file):
        logger.info(f"Loading streets from cache: {cache_file}")
        try:
            return gpd.read_file(cache_file)
        except Exception as e:
            logger.warning(f"Failed to load cached streets: {e}")
            # Continue to re-download
    
    logger.info(f"Downloading street network for {city}...")
    
    try:
        # Check if this is a legacy city with special handling
        if city.lower() in LEGACY_CITY_PARAMS and 'boroughs' in LEGACY_CITY_PARAMS[city.lower()]:
            return _load_legacy_city_network(city, cache_file)
        else:
            return _load_generic_city_network(city, cache_file)
            
    except Exception as e:
        logger.error(f"Failed to load street network for {city}: {e}")
        return gpd.GeoDataFrame(geometry=[], crs=DEFAULT_CRS)

def _load_generic_city_network(city: str, cache_file: str):
    """Load street network for any generic city."""
    try:
        # Download street network for the entire city/area
        logger.info(f"Downloading street network for {city}...")
        G = ox.graph_from_place(city, network_type='drive')
        
        # Convert to GeoDataFrame
        streets_gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
        
        # Process and save
        return _process_and_save_streets(streets_gdf, cache_file)
        
    except Exception as e:
        logger.error(f"Error loading streets for {city}: {e}")
        raise

def _load_legacy_city_network(city: str, cache_file: str):
    """Load street network for legacy cities with special borough handling."""
    params = LEGACY_CITY_PARAMS[city.lower()]
    
    if city.lower() == 'new_york':
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
    elif city.lower() == 'london':
        # Use boroughs from config
        areas = [f"{borough}, London, UK" for borough in params['boroughs']]
    else:
        # Fallback to generic loading
        return _load_generic_city_network(city, cache_file)
    
    all_streets = []
    
    for area in areas:
        logger.info(f"Loading streets for {area}...")
        try:
            # Download street network
            G = ox.graph_from_place(area, network_type='drive')
            
            # Convert to GeoDataFrame
            streets_gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
            all_streets.append(streets_gdf)
        except Exception as e:
            logger.warning(f"Error loading streets for {area}: {e}")
    
    if not all_streets:
        raise Exception("No street networks could be loaded")
    
    # Combine all street networks
    streets_gdf = gpd.GeoDataFrame(pd.concat(all_streets, ignore_index=True))
    
    return _process_and_save_streets(streets_gdf, cache_file)

def _process_and_save_streets(streets_gdf: gpd.GeoDataFrame, cache_file: str):
    """Process street data and save to cache."""
    # Create a unique ID for each street segment
    streets_gdf['street_id'] = range(len(streets_gdf))
    
    # Initialize coverage columns
    streets_gdf['covered'] = False
    streets_gdf['coverage_percent'] = 0.0
    
    # Ensure proper CRS
    if streets_gdf.crs is None:
        streets_gdf.set_crs(DEFAULT_CRS, inplace=True)
    
    # Save to file
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    streets_gdf.to_file(cache_file, driver='GeoJSON')
    logger.info(f"Cached street network with {len(streets_gdf)} segments")
    
    return streets_gdf 