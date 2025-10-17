# tests/test_visualization.py
import pytest
import numpy as np
import tempfile
import os
from src.visualization.map_generator import MapGenerator, HeatmapConfig, generate_heatmap

class TestMapGenerator:
    """Test cases for MapGenerator"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.generator = MapGenerator()
        
        # Create test data
        self.test_grid = np.array([
            [85.0, 90.0, 88.0],
            [82.0, 95.0, 91.0],
            [79.0, 87.0, 93.0]
        ])
        
        self.x_positions = np.array([0.0, 0.5, 1.0])
        self.y_positions = np.array([0.0, 0.5, 1.0])
    
    def test_initialization(self):
        """Test generator initialization"""
        assert isinstance(self.generator.config, HeatmapConfig)
        assert self.generator.config.figsize == (10, 8)
        assert self.generator.config.cmap == 'viridis'
    
    def test_custom_config(self):
        """Test generator with custom configuration"""
        config = HeatmapConfig(
            figsize=(8, 6),
            cmap='plasma',
            title='Test Heatmap'
        )
        
        generator = MapGenerator(config)
        assert generator.config.figsize == (8, 6)
        assert generator.config.cmap == 'plasma'
        assert generator.config.title == 'Test Heatmap'
    
    def test_heatmap_generation(self):
        """Test basic heatmap generation"""
        image_bytes = self.generator.generate_heatmap(
            self.test_grid,
            self.x_positions,
            self.y_positions,
            return_bytes=True
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
        assert image_bytes.startswith(b'\x89PNG')  # PNG header
    
    def test_heatmap_with_nans(self):
        """Test heatmap generation with NaN values"""
        grid_with_nans = self.test_grid.copy()
        grid_with_nans[1, 1] = np.nan
        
        image_bytes = self.generator.generate_heatmap(
            grid_with_nans,
            self.x_positions,
            self.y_positions,
            return_bytes=True
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
    
    def test_heatmap_file_output(self):
        """Test saving heatmap to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_heatmap.png")
            
            self.generator.generate_heatmap(
                self.test_grid,
                self.x_positions,
                self.y_positions,
                output_path=output_path,
                return_bytes=False
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
    
    def test_contour_map_generation(self):
        """Test contour map generation"""
        image_bytes = self.generator.generate_contour_map(
            self.test_grid,
            self.x_positions,
            self.y_positions,
            levels=5,
            return_bytes=True
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
        assert image_bytes.startswith(b'\x89PNG')
    
    def test_statistics_overlay(self):
        """Test statistics overlay generation"""
        image_bytes = self.generator.generate_statistics_overlay(
            self.test_grid,
            self.x_positions,
            self.y_positions,
            return_bytes=True
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
    
    def test_data_export_json(self):
        """Test JSON data export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_data")
            
            files = self.generator.export_data(
                self.test_grid,
                self.x_positions,
                self.y_positions,
                output_path,
                formats=["json"]
            )
            
            assert "json" in files
            assert os.path.exists(files["json"])
            
            # Verify JSON content
            import json
            with open(files["json"], 'r') as f:
                data = json.load(f)
            
            assert "grid" in data
            assert "x_positions" in data
            assert "y_positions" in data
            assert "statistics" in data
            assert data["shape"] == [3, 3]
    
    def test_data_export_csv(self):
        """Test CSV data export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_data")
            
            files = self.generator.export_data(
                self.test_grid,
                self.x_positions,
                self.y_positions,
                output_path,
                formats=["csv"]
            )
            
            assert "csv" in files
            assert os.path.exists(files["csv"])
            
            # Verify CSV content
            import csv
            with open(files["csv"], 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 9  # 3x3 grid
            assert "x_mm" in rows[0]
            assert "y_mm" in rows[0]
            assert "purity_percent" in rows[0]
    
    def test_data_export_npz(self):
        """Test NumPy compressed data export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_data")
            
            files = self.generator.export_data(
                self.test_grid,
                self.x_positions,
                self.y_positions,
                output_path,
                formats=["npz"]
            )
            
            assert "npz" in files
            assert os.path.exists(files["npz"])
            
            # Verify NPZ content
            loaded = np.load(files["npz"])
            assert "purity_grid" in loaded
            assert "x_positions" in loaded
            assert "y_positions" in loaded
            np.testing.assert_array_equal(loaded["purity_grid"], self.test_grid)
    
    def test_convenience_function(self):
        """Test convenience function"""
        image_bytes = generate_heatmap(
            self.test_grid,
            self.x_positions,
            self.y_positions
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        # Empty grid should raise an error or handle gracefully
        empty_grid = np.array([])
        
        with pytest.raises(Exception):
            self.generator.generate_heatmap(empty_grid, return_bytes=True)
    
    def test_custom_colormap_and_interpolation(self):
        """Test different colormaps and interpolation methods"""
        config = HeatmapConfig(
            cmap='plasma',
            interpolation='bilinear',
            vmin=80.0,
            vmax=95.0
        )
        
        generator = MapGenerator(config)
        image_bytes = generator.generate_heatmap(
            self.test_grid,
            self.x_positions,
            self.y_positions,
            return_bytes=True
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
    
    def test_grid_without_positions(self):
        """Test heatmap generation without position arrays"""
        image_bytes = self.generator.generate_heatmap(
            self.test_grid,
            return_bytes=True
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
