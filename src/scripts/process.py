#!/usr/bin/env python3
"""
Main script for processing walking data and generating street coverage maps.
"""
import os
import sys
from pathlib import Path
import geopandas as gpd
from ..data.walk_processor import process_walk_files, analyze_walks
from ..data.street_loader import load_street_network
from ..utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def main():
    """Main function to process walks and generate coverage maps."""
    # Create output directory
    Path(PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # Process walk files
    print("Processing walk files...")
    walks_gdf = process_walk_files(RAW_DATA_DIR)
    if walks_gdf.empty:
        print("No valid walks found.")
        sys.exit(1)
    
    # Save processed walks
    walks_file = Path(PROCESSED_DATA_DIR) / "processed_walks.geojson"
    walks_gdf.to_file(walks_file, driver='GeoJSON')
    print(f"Saved {len(walks_gdf)} walks to {walks_file}")
    
    # Load street network
    print("\nLoading street network...")
    streets_gdf = load_street_network()
    if streets_gdf.empty:
        print("No street network could be loaded.")
        sys.exit(1)
    
    # Analyze walks and calculate coverage
    print("\nAnalyzing walks and calculating coverage...")
    streets_with_coverage, valid_walks = analyze_walks(walks_gdf, streets_gdf)
    
    # Save results
    coverage_file = Path(PROCESSED_DATA_DIR) / "street_coverage.geojson"
    streets_with_coverage.to_file(coverage_file, driver='GeoJSON')
    print(f"\nSaved street coverage data to {coverage_file}")
    
    # Print summary
    total_streets = len(streets_with_coverage)
    covered_streets = streets_with_coverage[streets_with_coverage['covered']]
    coverage_percent = len(covered_streets) / total_streets * 100
    
    print("\nCoverage Summary:")
    print(f"Total streets: {total_streets}")
    print(f"Covered streets: {len(covered_streets)} ({coverage_percent:.1f}%)")
    print(f"Total walk distance: {valid_walks.geometry.length.sum() / 1000:.1f} km")

if __name__ == '__main__':
    main() 