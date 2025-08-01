#!/usr/bin/env python3
"""
Main script for processing walking data and generating street coverage maps.
"""
import os
import sys
import argparse
import logging
from pathlib import Path
import geopandas as gpd
from ..data.walk_processor import process_walk_files, analyze_walks
from ..data.street_loader import load_street_network
from ..utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, METRIC_CRS, get_city_parameters
from ..utils.city_analyzer import validate_city_name

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('processing.log')
    ]
)

def main():
    """Main function to process walks and generate coverage maps."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Process walking data and generate street coverage maps for any city worldwide.',
        epilog="""
Examples:
  python -m src.scripts.process --city "New York City, NY, USA"
  python -m src.scripts.process --city "London, UK"
  python -m src.scripts.process --city "Paris, France"
  python -m src.scripts.process --city "Tokyo, Japan"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--city', type=str, default='new_york',
                      help='City to process (can be any city worldwide, e.g., "Paris, France")')
    parser.add_argument('--validate-only', action='store_true',
                      help='Only validate that the city can be processed, don\'t run full analysis')
    parser.add_argument('--force-reanalysis', action='store_true',
                      help='Force re-analysis of city parameters even if cached')
    args = parser.parse_args()
    
    city = args.city
    print(f"\nProcessing data for {city}...")
    
    # Validate city name first
    print("Validating city name and availability...")
    
    # Check if it's a legacy city first (no internet needed)
    from ..utils.config import LEGACY_CITY_PARAMS
    if city.lower() in LEGACY_CITY_PARAMS:
        print(f"✓ Using legacy configuration for '{city}'")
    else:
        # For new cities, validate with internet
        try:
            if not validate_city_name(city):
                print(f"Error: Could not find street network data for '{city}'.")
                print("This could be due to:")
                print("- Internet connection issues")
                print("- City name not recognized by OpenStreetMap")
                print("- City too small or lacking street data")
                print("\nPlease try:")
                print("- Adding country/state information (e.g., 'Paris, France')")
                print("- Checking spelling")
                print("- Using a larger metropolitan area name")
                print("- Checking your internet connection")
                print("\nFor testing without internet, try legacy cities:")
                print("- python -m src.scripts.process --city new_york")
                print("- python -m src.scripts.process --city london")
                sys.exit(1)
        except Exception as e:
            print(f"Error during city validation: {e}")
            print("This might be a network connectivity issue.")
            print("Try again later or use legacy cities: 'new_york' or 'london'")
            sys.exit(1)
    
    print(f"✓ City '{city}' is valid and ready for processing.")
    
    if args.validate_only:
        print("Validation complete. Use without --validate-only to process data.")
        return
    
    # Get city parameters (will auto-analyze if needed)
    print("Analyzing city characteristics...")
    if args.force_reanalysis:
        # Clear cache for this city
        cache_dir = Path(PROCESSED_DATA_DIR) / 'city_cache'
        clean_name = city.lower().replace(' ', '_').replace(',', '')
        cache_file = cache_dir / f"{clean_name}_params.json"
        if cache_file.exists():
            cache_file.unlink()
            print("Cleared cached parameters, will re-analyze.")
    
    try:
        city_params = get_city_parameters(city)
        print(f"✓ City analysis complete. Using buffer distance: {city_params['buffer_distance']}m")
    except Exception as e:
        print(f"Warning: City analysis failed ({e})")
        print("Falling back to default parameters...")
        from ..utils.config import get_default_parameters
        city_params = get_default_parameters()
        print(f"Using default buffer distance: {city_params['buffer_distance']}m")
    
    # Create output directory
    Path(PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # Process walk files
    print("Processing walk files...")
    walks_gdf = process_walk_files(RAW_DATA_DIR)
    if walks_gdf.empty:
        print("No valid walks found.")
        print("Make sure you have .tcx files in the data/raw/ directory.")
        print("See the README for instructions on how to export data from Google Fit.")
        sys.exit(1)
    
    # Clean city name for filenames
    clean_city_name = city.lower().replace(' ', '_').replace(',', '').replace('/', '_')
    
    # Save processed walks
    walks_file = Path(PROCESSED_DATA_DIR) / f"processed_walks_{clean_city_name}.geojson"
    walks_gdf.to_file(walks_file, driver='GeoJSON')
    print(f"Saved {len(walks_gdf)} walks to {walks_file}")
    
    # Load street network
    print("\nLoading street network...")
    try:
        streets_gdf = load_street_network(city)
        if streets_gdf.empty:
            print("No street network could be loaded.")
            print("This could be due to:")
            print("- Internet connectivity issues")
            print("- City boundaries not well-defined in OpenStreetMap")
            print("- Very small city with limited street data")
            print("\nTry:")
            print("- Using a larger nearby city or metropolitan area")
            print("- Checking your internet connection")
            print("- Using legacy cities for testing: 'new_york' or 'london'")
            sys.exit(1)
        print(f"✓ Loaded street network with {len(streets_gdf):,} street segments")
    except Exception as e:
        print(f"Error loading street network: {e}")
        print("This is likely a network connectivity issue.")
        print("Please check your internet connection and try again.")
        sys.exit(1)
    
    # Analyze walks and calculate coverage
    print("\nAnalyzing walks and calculating coverage...")
    streets_with_coverage, valid_walks = analyze_walks(walks_gdf, streets_gdf, city)
    
    # Save results
    coverage_file = Path(PROCESSED_DATA_DIR) / f"street_coverage_{clean_city_name}.geojson"
    streets_with_coverage.to_file(coverage_file, driver='GeoJSON')
    print(f"\nSaved street coverage data to {coverage_file}")
    
    # Print summary
    total_streets = len(streets_with_coverage)
    covered_streets = streets_with_coverage[streets_with_coverage['covered']]
    coverage_percent = len(covered_streets) / total_streets * 100 if total_streets > 0 else 0
    
    print("\n" + "="*50)
    print("COVERAGE SUMMARY")
    print("="*50)
    print(f"City: {city}")
    print(f"Total streets: {total_streets:,}")
    print(f"Covered streets: {len(covered_streets):,} ({coverage_percent:.1f}%)")
    
    # Calculate total walk distance in metric CRS
    if not valid_walks.empty:
        valid_walks_metric = valid_walks.to_crs(METRIC_CRS)
        total_distance_km = valid_walks_metric.geometry.length.sum() / 1000
        print(f"Total walk distance: {total_distance_km:.1f} km")
    
    print("\nFiles generated:")
    print(f"- {walks_file}")
    print(f"- {coverage_file}")
    print("\nUpload these files to kepler.gl to visualize your coverage!")

if __name__ == '__main__':
    main() 