# tests/test_scan_orchestrator.py
import pytest
import numpy as np
import asyncio
from unittest.mock import Mock, AsyncMock
from src.core.scan_orchestrator import ScanOrchestrator, ScanParameters, ScanStatus
from src.hardware.stage_controller import StageController, StageConfig
from src.hardware.spectrometer import SpectrometerController, SpectrometerConfig

class TestScanOrchestrator:
    """Test cases for ScanOrchestrator"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Create mock hardware
        self.stage = StageController(StageConfig(x_max_mm=10.0, y_max_mm=10.0))
        self.stage.connect()
        self.stage.home()
        
        self.spectrometer = SpectrometerController(SpectrometerConfig())
        self.spectrometer.connect()
        
        # Create mock inference engine
        self.inference_engine = Mock()
        self.inference_engine.predict = AsyncMock(return_value={
            "purity_percentage": 85.0,
            "confidence_score": 0.9
        })
        
        self.orchestrator = ScanOrchestrator(
            stage=self.stage,
            spectrometer=self.spectrometer,
            inference_engine=self.inference_engine
        )
    
    def test_initialization(self):
        """Test orchestrator initialization"""
        assert self.orchestrator.stage == self.stage
        assert self.orchestrator.spectrometer == self.spectrometer
        assert self.orchestrator.status == ScanStatus.IDLE
        assert self.orchestrator.current_scan is None
    
    def test_scan_parameters_validation(self):
        """Test scan parameter validation"""
        # Valid parameters
        params = ScanParameters(
            x_start=0.0, y_start=0.0,
            x_end=2.0, y_end=2.0,
            step_x=0.5, step_y=0.5
        )
        
        # This should not raise an error
        self.orchestrator._validate_scan_parameters(params)
        
        # Invalid parameters - x_start >= x_end
        invalid_params = ScanParameters(
            x_start=2.0, y_start=0.0,
            x_end=1.0, y_end=2.0,
            step_x=0.5, step_y=0.5
        )
        
        with pytest.raises(ValueError, match="x_start must be less than x_end"):
            self.orchestrator._validate_scan_parameters(invalid_params)
        
        # Invalid parameters - negative step
        invalid_params = ScanParameters(
            x_start=0.0, y_start=0.0,
            x_end=2.0, y_end=2.0,
            step_x=-0.5, step_y=0.5
        )
        
        with pytest.raises(ValueError, match="Step sizes must be positive"):
            self.orchestrator._validate_scan_parameters(invalid_params)
        
        # Invalid parameters - out of bounds
        invalid_params = ScanParameters(
            x_start=0.0, y_start=0.0,
            x_end=15.0, y_end=2.0,  # x_end > stage limit
            step_x=0.5, step_y=0.5
        )
        
        with pytest.raises(ValueError, match="X range .* outside stage limits"):
            self.orchestrator._validate_scan_parameters(invalid_params)
    
    @pytest.mark.asyncio
    async def test_scan_grid_calculation(self):
        """Test scan grid size calculation"""
        params = ScanParameters(
            x_start=0.0, y_start=0.0,
            x_end=2.0, y_end=1.0,
            step_x=0.5, step_y=0.5
        )
        
        # Calculate expected grid size
        # x: 0.0, 0.5, 1.0, 1.5, 2.0 = 5 points
        # y: 0.0, 0.5, 1.0 = 3 points
        # Total: 5 * 3 = 15 points
        
        result = await self.orchestrator.start_scan(params)
        
        assert result.total_points == 15
        assert len(result.x_positions) == 5
        assert len(result.y_positions) == 3
        assert result.grid.shape == (3, 5)  # (ny, nx)
    
    @pytest.mark.asyncio
    async def test_small_scan_execution(self):
        """Test execution of a small scan"""
        params = ScanParameters(
            x_start=0.0, y_start=0.0,
            x_end=1.0, y_end=1.0,
            step_x=1.0, step_y=1.0,
            integration_time=0.01  # Fast scan for testing
        )
        
        result = await self.orchestrator.start_scan(params)
        
        # Should have 2x2 = 4 points
        assert result.total_points == 4
        assert result.completed_points == 4
        assert result.status == ScanStatus.COMPLETED
        assert result.end_time is not None
        
        # Check that inference was called for each point
        assert self.inference_engine.predict.call_count == 4
        
        # Check grid has expected values
        assert not np.isnan(result.grid).all()  # Should have some valid values
    
    @pytest.mark.asyncio
    async def test_scan_cancellation(self):
        """Test scan cancellation"""
        params = ScanParameters(
            x_start=0.0, y_start=0.0,
            x_end=3.0, y_end=3.0,
            step_x=0.5, step_y=0.5,
            integration_time=0.1
        )
        
        # Start scan in background
        scan_task = asyncio.create_task(self.orchestrator.start_scan(params))
        
        # Wait a bit then cancel
        await asyncio.sleep(0.1)
        await self.orchestrator.cancel_scan()
        
        # Wait for scan to complete
        result = await scan_task
        
        assert result.status == ScanStatus.CANCELLED
        assert result.completed_points < result.total_points
    
    def test_progress_callbacks(self):
        """Test progress callback functionality"""
        callback_calls = []
        
        def progress_callback(scan_result):
            callback_calls.append(scan_result.completed_points)
        
        self.orchestrator.add_progress_callback(progress_callback)
        
        # Simulate progress notification
        self.orchestrator.current_scan = Mock()
        self.orchestrator.current_scan.completed_points = 5
        self.orchestrator._notify_progress()
        
        assert len(callback_calls) == 1
        assert callback_calls[0] == 5
        
        # Remove callback
        self.orchestrator.remove_progress_callback(progress_callback)
        self.orchestrator._notify_progress()
        
        # Should not have been called again
        assert len(callback_calls) == 1
    
    def test_scan_status_reporting(self):
        """Test scan status reporting"""
        # Initially idle
        status = self.orchestrator.get_scan_status()
        assert status["status"] == "idle"
        
        # Mock an active scan
        self.orchestrator.status = ScanStatus.RUNNING
        self.orchestrator.current_scan = Mock()
        self.orchestrator.current_scan.completed_points = 5
        self.orchestrator.current_scan.total_points = 10
        self.orchestrator.current_scan.start_time = 1000.0
        self.orchestrator.current_scan.error_message = None
        
        status = self.orchestrator.get_scan_status()
        assert status["status"] == "running"
        assert status["progress"] == 0.5
        assert status["completed_points"] == 5
        assert status["total_points"] == 10
    
    @pytest.mark.asyncio
    async def test_hardware_preparation(self):
        """Test hardware preparation before scanning"""
        # Test with unhomed stage
        unhomed_stage = StageController(StageConfig())
        unhomed_stage.connect()
        # Don't home
        
        orchestrator = ScanOrchestrator(
            stage=unhomed_stage,
            spectrometer=self.spectrometer,
            inference_engine=self.inference_engine
        )
        
        # Should home the stage during preparation
        await orchestrator._prepare_hardware()
        assert unhomed_stage.is_homed == True
    
    def test_export_functionality(self):
        """Test scan data export"""
        # Mock a completed scan
        self.orchestrator.current_scan = Mock()
        self.orchestrator.current_scan.parameters = ScanParameters(
            x_start=0.0, y_start=0.0, x_end=1.0, y_end=1.0,
            step_x=0.5, step_y=0.5
        )
        self.orchestrator.current_scan.grid = np.array([[85.0, 90.0], [88.0, 92.0]])
        self.orchestrator.current_scan.x_positions = [0.0, 0.5]
        self.orchestrator.current_scan.y_positions = [0.0, 0.5]
        self.orchestrator.current_scan.status = ScanStatus.COMPLETED
        self.orchestrator.current_scan.start_time = 1000.0
        self.orchestrator.current_scan.end_time = 1010.0
        self.orchestrator.current_scan.total_points = 4
        self.orchestrator.current_scan.completed_points = 4
        self.orchestrator.current_scan.points = []
        
        # Test export (would normally write to file)
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = os.path.join(temp_dir, "test_scan")
            
            # This should not raise an error
            self.orchestrator.export_scan_data(export_path, "json")
            
            # Check that file was created
            assert os.path.exists(f"{export_path}.json")
