"""
Auto-detection and analysis of city characteristics for optimal processing parameters.
"""
import geopandas as gpd
import osmnx as ox
import numpy as np
from shapely.geometry import Point, box
from typing import Dict, Optional, Tuple, List
import logging
from .config import DEFAULT_CRS, METRIC_CRS

logger = logging.getLogger(__name__)

class CityAnalyzer:
    """Analyzes city characteristics to determine optimal processing parameters."""
    
    def __init__(self, city_name: str):
        """Initialize city analyzer with city name."""
        self.city_name = city_name
        self.street_network = None
        self.characteristics = {}
        
    def analyze_city(self) -> Dict:
        """
        Analyze city characteristics and return optimal parameters.
        
        Returns:
            Dict containing optimized parameters for the city
        """
        logger.info(f"Analyzing characteristics for {self.city_name}...")
        
        try:
            # Download street network
            self._download_street_network()
            
            # Analyze street characteristics
            self._analyze_street_density()
            self._analyze_urban_structure()
            self._analyze_intersection_complexity()
            
            # Calculate optimal parameters
            return self._calculate_optimal_parameters()
            
        except Exception as e:
            logger.warning(f"Error analyzing {self.city_name}: {e}")
            return self._get_default_parameters()
    
    def _download_street_network(self):
        """Download street network for the city."""
        try:
            # Try to get the city as a place
            logger.info(f"Downloading street network for {self.city_name}...")
            graph = ox.graph_from_place(self.city_name, network_type='drive')
            self.street_network = ox.graph_to_gdfs(graph, nodes=False, edges=True)
            
            # Store bounding box
            bounds = self.street_network.bounds
            self.characteristics['bbox'] = [
                bounds.minx.min(), bounds.miny.min(),
                bounds.maxx.max(), bounds.maxy.max()
            ]
            
        except Exception as e:
            logger.error(f"Failed to download street network for {self.city_name}: {e}")
            raise
    
    def _analyze_street_density(self):
        """Analyze street density to determine GPS buffer requirements."""
        if self.street_network is None:
            return
            
        # Convert to metric CRS for accurate calculations
        streets_metric = self.street_network.to_crs(METRIC_CRS)
        
        # Calculate total street length
        total_length = streets_metric.geometry.length.sum()
        
        # Calculate area (using convex hull of street network)
        area = streets_metric.geometry.unary_union.convex_hull.area
        
        # Street density (meters of street per square meter)
        street_density = total_length / area if area > 0 else 0
        
        self.characteristics['street_density'] = street_density
        self.characteristics['total_street_length'] = total_length
        self.characteristics['area'] = area
        
        logger.info(f"Street density: {street_density:.6f} m/m²")
    
    def _analyze_urban_structure(self):
        """Analyze urban structure (grid vs organic layout)."""
        if self.street_network is None:
            return
            
        # Convert to metric CRS
        streets_metric = self.street_network.to_crs(METRIC_CRS)
        
        # Calculate street orientations
        orientations = []
        for geom in streets_metric.geometry:
            if geom.geom_type == 'LineString':
                coords = list(geom.coords)
                if len(coords) >= 2:
                    # Calculate bearing of each segment
                    for i in range(len(coords) - 1):
                        x1, y1 = coords[i]
                        x2, y2 = coords[i + 1]
                        bearing = np.arctan2(y2 - y1, x2 - x1)
                        orientations.append(np.degrees(bearing) % 180)  # Normalize to 0-180
        
        if orientations:
            orientations = np.array(orientations)
            
            # Check for grid pattern (peaks at 0° and 90°)
            hist, bins = np.histogram(orientations, bins=18, range=(0, 180))
            
            # Look for peaks around 0°, 45°, 90°, 135°
            grid_indicators = [
                hist[0] + hist[-1],  # 0° and 180° (same direction)
                hist[4:6].sum(),     # Around 45°
                hist[8:10].sum(),    # Around 90°
                hist[13:15].sum()    # Around 135°
            ]
            
            # Grid score: higher if streets align to cardinal/diagonal directions
            total_count = len(orientations)
            grid_score = sum(grid_indicators) / total_count if total_count > 0 else 0
            
            self.characteristics['grid_score'] = grid_score
            self.characteristics['is_grid'] = grid_score > 0.4  # Threshold for grid detection
            
            logger.info(f"Grid score: {grid_score:.3f}, Is grid: {grid_score > 0.4}")
    
    def _analyze_intersection_complexity(self):
        """Analyze intersection complexity."""
        if self.street_network is None:
            return
            
        try:
            # Get the original graph to analyze intersections
            graph = ox.graph_from_place(self.city_name, network_type='drive')
            nodes, edges = ox.graph_to_gdfs(graph)
            
            # Count intersection types
            intersection_counts = nodes['street_count'].value_counts().to_dict()
            
            # Calculate complexity metrics
            total_intersections = len(nodes)
            complex_intersections = sum(count for degree, count in intersection_counts.items() if degree > 4)
            
            complexity_ratio = complex_intersections / total_intersections if total_intersections > 0 else 0
            
            self.characteristics['intersection_complexity'] = complexity_ratio
            self.characteristics['total_intersections'] = total_intersections
            self.characteristics['intersection_distribution'] = intersection_counts
            
            logger.info(f"Intersection complexity: {complexity_ratio:.3f}")
            
        except Exception as e:
            logger.warning(f"Failed to analyze intersections: {e}")
            self.characteristics['intersection_complexity'] = 0.2  # Default moderate complexity
    
    def _calculate_optimal_parameters(self) -> Dict:
        """Calculate optimal parameters based on city characteristics."""
        params = self._get_default_parameters()
        
        # Adjust buffer distance based on street density
        street_density = self.characteristics.get('street_density', 0.001)
        
        if street_density > 0.005:  # Very dense (like Manhattan)
            params['buffer_distance'] = 3
        elif street_density > 0.002:  # Dense urban
            params['buffer_distance'] = 5
        elif street_density > 0.001:  # Moderate density
            params['buffer_distance'] = 8
        else:  # Low density/suburban
            params['buffer_distance'] = 12
        
        # Adjust speed thresholds based on urban structure
        if self.characteristics.get('is_grid', False):
            # Grid cities often have more consistent walking patterns
            params['max_walking_speed'] = 3.5
            params['min_walking_speed'] = 0.2
        else:
            # Organic cities may have more varied walking patterns
            params['max_walking_speed'] = 3.0
            params['min_walking_speed'] = 0.1
        
        # Adjust sinuosity based on intersection complexity
        complexity = self.characteristics.get('intersection_complexity', 0.2)
        if complexity > 0.3:
            params['max_sinuosity'] = 5.0  # Allow more winding paths
        else:
            params['max_sinuosity'] = 3.5
        
        # Set bounding box
        if 'bbox' in self.characteristics:
            params['bbox'] = self.characteristics['bbox']
        
        # Log the calculated parameters
        logger.info(f"Calculated parameters for {self.city_name}:")
        for key, value in params.items():
            logger.info(f"  {key}: {value}")
        
        return params
    
    def _get_default_parameters(self) -> Dict:
        """Get default parameters as fallback."""
        return {
            'buffer_distance': 8,
            'max_walking_speed': 3.0,
            'min_walking_speed': 0.1,
            'max_sinuosity': 4.0,
            'max_direct_distance': 15000,
            'bbox': None  # Will be set from street network bounds
        }

def get_city_parameters(city_name: str, cache_dir: str = None) -> Dict:
    """
    Get optimized parameters for any city.
    
    Args:
        city_name: Name of the city to analyze
        cache_dir: Directory to cache analysis results
        
    Returns:
        Dictionary of optimized parameters for the city
    """
    # Clean up city name for caching
    clean_name = city_name.lower().replace(' ', '_').replace(',', '')
    
    # Try to load from cache if available
    if cache_dir:
        import os
        import json
        cache_file = os.path.join(cache_dir, f"{clean_name}_params.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    params = json.load(f)
                logger.info(f"Loaded cached parameters for {city_name}")
                return params
            except Exception as e:
                logger.warning(f"Failed to load cached parameters: {e}")
    
    # Analyze the city
    analyzer = CityAnalyzer(city_name)
    params = analyzer.analyze_city()
    
    # Cache the results
    if cache_dir:
        try:
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(params, f, indent=2)
            logger.info(f"Cached parameters for {city_name}")
        except Exception as e:
            logger.warning(f"Failed to cache parameters: {e}")
    
    return params

def validate_city_name(city_name: str) -> bool:
    """
    Validate if a city name can be processed.
    
    Args:
        city_name: Name of the city to validate
        
    Returns:
        True if city can be processed, False otherwise
    """
    try:
        # Try a simple test query with timeout
        import osmnx as ox
        # Set a shorter timeout for validation
        old_timeout = ox.settings.timeout
        ox.settings.timeout = 30  # 30 seconds timeout
        
        test_graph = ox.graph_from_place(city_name, network_type='drive')
        
        # Restore original timeout
        ox.settings.timeout = old_timeout
        
        return len(test_graph.nodes) > 10  # Must have at least some street network
    except Exception as e:
        # Log the specific error for debugging
        logger.debug(f"City validation failed for '{city_name}': {e}")
        return False