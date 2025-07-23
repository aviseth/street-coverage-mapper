"""Tests for walk processor module."""
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from datetime import datetime
from shapely.geometry import LineString, Point
import geopandas as gpd
from src.data.walk_processor import parse_tcx_file, process_walk_files, analyze_walks


class TestWalkProcessor(unittest.TestCase):
    """Test walk processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_tcx = """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">
  <Activities>
    <Activity Sport="Walking">
      <Lap>
        <Track>
          <Trackpoint>
            <Time>2024-01-01T10:00:00Z</Time>
            <Position>
              <LatitudeDegrees>40.7128</LatitudeDegrees>
              <LongitudeDegrees>-74.0060</LongitudeDegrees>
            </Position>
          </Trackpoint>
          <Trackpoint>
            <Time>2024-01-01T10:01:00Z</Time>
            <Position>
              <LatitudeDegrees>40.7130</LatitudeDegrees>
              <LongitudeDegrees>-74.0062</LongitudeDegrees>
            </Position>
          </Trackpoint>
        </Track>
      </Lap>
    </Activity>
  </Activities>
</TrainingCenterDatabase>"""
    
    def test_parse_tcx_file_valid(self):
        """Test parsing a valid TCX file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tcx', delete=False) as f:
            f.write(self.sample_tcx)
            f.flush()
            
            result = parse_tcx_file(f.name)
            
            self.assertIsNotNone(result)
            self.assertIsInstance(result['geometry'], LineString)
            self.assertEqual(len(result['geometry'].coords), 2)
            self.assertIsInstance(result['start_time'], datetime)
            self.assertIsInstance(result['end_time'], datetime)
            
            os.unlink(f.name)
    
    def test_parse_tcx_file_invalid_sport(self):
        """Test parsing TCX file with non-walking activity."""
        invalid_tcx = self.sample_tcx.replace('Sport="Walking"', 'Sport="Running"')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tcx', delete=False) as f:
            f.write(invalid_tcx)
            f.flush()
            
            result = parse_tcx_file(f.name)
            self.assertIsNone(result)
            
            os.unlink(f.name)
    
    def test_analyze_walks_filtering(self):
        """Test walk filtering in analyze_walks."""
        # Create sample walks GeoDataFrame
        walks_data = [{
            'geometry': LineString([(0, 0), (0.001, 0.001)]),
            'start_time': datetime(2024, 1, 1, 10, 0),
            'end_time': datetime(2024, 1, 1, 10, 5),
            'source_file': 'test.tcx'
        }]
        walks_gdf = gpd.GeoDataFrame(walks_data, crs='EPSG:4326')
        
        # Create sample streets GeoDataFrame
        streets_data = [{
            'geometry': LineString([(0, 0), (0.001, 0)]),
            'street_id': 1,
            'covered': False,
            'coverage_percent': 0.0
        }]
        streets_gdf = gpd.GeoDataFrame(streets_data, crs='EPSG:4326')
        
        # Analyze walks
        covered_streets, valid_walks = analyze_walks(walks_gdf, streets_gdf, 'new_york')
        
        self.assertIsInstance(covered_streets, gpd.GeoDataFrame)
        self.assertIsInstance(valid_walks, gpd.GeoDataFrame)
    
    def test_process_walk_files_empty_directory(self):
        """Test processing an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_walk_files(tmpdir)
            self.assertTrue(result.empty)


if __name__ == '__main__':
    unittest.main()