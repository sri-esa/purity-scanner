# tests/test_stage_controller.py
import pytest
import numpy as np
from src.hardware.stage_controller import StageController, StageConfig

class TestStageController:
    """Test cases for StageController"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.config = StageConfig(x_max_mm=10.0, y_max_mm=10.0)
        self.stage = StageController(self.config)
        self.stage.connect()  # Mock connection
        self.stage.home()     # Mock homing
    
    def test_initialization(self):
        """Test stage controller initialization"""
        assert self.stage.config.x_max_mm == 10.0
        assert self.stage.config.y_max_mm == 10.0
        assert self.stage.x == 0.0
        assert self.stage.y == 0.0
        assert self.stage.is_connected == True
        assert self.stage.is_homed == True
    
    def test_absolute_movement(self):
        """Test absolute movement within bounds"""
        # Valid movement
        pos = self.stage.move_abs(5.0, 3.0)
        assert pos == (5.0, 3.0)
        assert self.stage.get_position() == (5.0, 3.0)
        
        # Movement to origin
        pos = self.stage.move_abs(0.0, 0.0)
        assert pos == (0.0, 0.0)
        
        # Movement to max bounds
        pos = self.stage.move_abs(10.0, 10.0)
        assert pos == (10.0, 10.0)
    
    def test_relative_movement(self):
        """Test relative movement"""
        # Start at origin
        self.stage.move_abs(0.0, 0.0)
        
        # Move relative
        pos = self.stage.move_rel(2.0, 3.0)
        assert pos == (2.0, 3.0)
        
        # Move relative again
        pos = self.stage.move_rel(1.0, -1.0)
        assert pos == (3.0, 2.0)
    
    def test_movement_bounds_validation(self):
        """Test that movements outside bounds raise errors"""
        # X out of bounds
        with pytest.raises(ValueError, match="X position .* outside bounds"):
            self.stage.move_abs(-1.0, 5.0)
        
        with pytest.raises(ValueError, match="X position .* outside bounds"):
            self.stage.move_abs(11.0, 5.0)
        
        # Y out of bounds
        with pytest.raises(ValueError, match="Y position .* outside bounds"):
            self.stage.move_abs(5.0, -1.0)
        
        with pytest.raises(ValueError, match="Y position .* outside bounds"):
            self.stage.move_abs(5.0, 11.0)
    
    def test_movement_without_homing(self):
        """Test that movement without homing raises error"""
        unhomed_stage = StageController(self.config)
        unhomed_stage.connect()
        # Don't call home()
        
        with pytest.raises(RuntimeError, match="Stage not homed"):
            unhomed_stage.move_abs(1.0, 1.0)
    
    def test_movement_without_connection(self):
        """Test that movement without connection raises error"""
        disconnected_stage = StageController(self.config)
        # Don't call connect()
        
        with pytest.raises(RuntimeError, match="Stage not connected"):
            disconnected_stage.move_abs(1.0, 1.0)
    
    def test_emergency_stop(self):
        """Test emergency stop functionality"""
        self.stage.stop()
        assert self.stage.emergency_stop == True
        
        # Movement should fail after emergency stop
        with pytest.raises(RuntimeError, match="Emergency stop active"):
            self.stage.move_abs(1.0, 1.0)
        
        # Reset emergency stop
        self.stage.reset_emergency_stop()
        assert self.stage.emergency_stop == False
        
        # Movement should work again
        pos = self.stage.move_abs(1.0, 1.0)
        assert pos == (1.0, 1.0)
    
    def test_speed_setting(self):
        """Test speed setting validation"""
        # Valid speed
        self.stage.set_speed(5.0)
        
        # Invalid speeds
        with pytest.raises(ValueError, match="Speed must be between"):
            self.stage.set_speed(0.0)
        
        with pytest.raises(ValueError, match="Speed must be between"):
            self.stage.set_speed(-1.0)
        
        with pytest.raises(ValueError, match="Speed must be between"):
            self.stage.set_speed(100.0)  # Assuming max is 10.0
    
    def test_get_limits(self):
        """Test getting stage limits"""
        limits = self.stage.get_limits()
        assert limits == ((0.0, 10.0), (0.0, 10.0))
    
    def test_context_manager(self):
        """Test using stage as context manager"""
        config = StageConfig(x_max_mm=5.0, y_max_mm=5.0)
        
        with StageController(config) as stage:
            assert stage.is_connected == True
            stage.home()
            pos = stage.move_abs(1.0, 1.0)
            assert pos == (1.0, 1.0)
        
        # Should be disconnected after context exit
        assert stage.is_connected == False
