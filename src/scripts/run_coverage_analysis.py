#!/usr/bin/env python3

import geopandas as gpd
from src.data.walk_processor import analyze_walks
from src.utils.config import CITY_PARAMS

def main():
    # Load the processed walks and streets GeoJSON files
    walks_gdf = gpd.read_file('data/processed/processed_walks_london.geojson')
    streets_gdf = gpd.read_file('data/processed/london_streets.geojson')

    # Specify the city
    city = 'london'

    # Analyze walks and calculate street coverage
    streets_with_coverage, valid_walks = analyze_walks(walks_gdf, streets_gdf, city)

    # Save the coverage results to a new GeoJSON file
    coverage_file = f'data/processed/street_coverage_{city}.geojson'
    streets_with_coverage.to_file(coverage_file, driver='GeoJSON')

    print(f"Coverage analysis completed. Results saved to {coverage_file}")

if __name__ == "__main__":
    main() 