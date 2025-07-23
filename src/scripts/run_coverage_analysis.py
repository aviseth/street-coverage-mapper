#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import geopandas as gpd
from src.data.walk_processor import analyze_walks
from src.utils.config import CITY_PARAMS

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Re-run coverage analysis on existing processed data.')
    parser.add_argument('--city', choices=list(CITY_PARAMS.keys()), default='new_york',
                      help='City to process (default: new_york)')
    args = parser.parse_args()
    
    city = args.city
    
    # Load the processed walks and streets GeoJSON files
    walks_file = f'data/processed/processed_walks_{city}.geojson'
    streets_file = f'data/processed/{city}_streets.geojson'
    
    if not Path(walks_file).exists():
        print(f"Error: {walks_file} not found. Run process.py first.")
        sys.exit(1)
    
    if not Path(streets_file).exists():
        print(f"Error: {streets_file} not found. Run process.py first.")
        sys.exit(1)
    
    walks_gdf = gpd.read_file(walks_file)
    streets_gdf = gpd.read_file(streets_file)

    # Analyze walks and calculate street coverage
    streets_with_coverage, valid_walks = analyze_walks(walks_gdf, streets_gdf, city)

    # Save the coverage results to a new GeoJSON file
    coverage_file = f'data/processed/street_coverage_{city}.geojson'
    streets_with_coverage.to_file(coverage_file, driver='GeoJSON')

    print(f"Coverage analysis completed. Results saved to {coverage_file}")

if __name__ == "__main__":
    main() 