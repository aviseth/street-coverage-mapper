"""Tests for configuration module."""
import unittest
from src.utils.config import CITY_PARAMS, DEFAULT_CRS, METRIC_CRS


class TestConfig(unittest.TestCase):
    """Test configuration settings."""
    
    def test_city_params_exist(self):
        """Test that city parameters are defined."""
        self.assertIn('new_york', CITY_PARAMS)
        self.assertIn('london', CITY_PARAMS)
    
    def test_city_params_structure(self):
        """Test that city parameters have required fields."""
        for city, params in CITY_PARAMS.items():
            self.assertIn('buffer_distance', params)
            self.assertIn('max_walking_speed', params)
            self.assertIn('min_walking_speed', params)
            self.assertIn('max_sinuosity', params)
            self.assertIn('max_direct_distance', params)
            self.assertIn('bbox', params)
            
            # Test bbox structure
            self.assertEqual(len(params['bbox']), 4)
            self.assertIsInstance(params['bbox'], list)
    
    def test_london_boroughs(self):
        """Test that London has boroughs defined."""
        self.assertIn('boroughs', CITY_PARAMS['london'])
        self.assertGreater(len(CITY_PARAMS['london']['boroughs']), 0)
    
    def test_crs_settings(self):
        """Test CRS settings are valid."""
        self.assertEqual(DEFAULT_CRS, 'EPSG:4326')
        self.assertEqual(METRIC_CRS, 'EPSG:3857')


if __name__ == '__main__':
    unittest.main()