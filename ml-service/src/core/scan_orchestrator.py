# src/core/scan_orchestrator.py
import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.hardware.stage_controller import StageController
from src.hardware.spectrometer import SpectrometerController
from src.core.inference import InferenceEngine
from src.core.preprocessing import SpectrumPreprocessor

logger = logging.getLogger(__name__)

class ScanStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class ScanParameters:
    """Parameters for a 2D scan"""
    x_start: float  # mm
    y_start: float  # mm
    x_end: float    # mm
    y_end: float    # mm
    step_x: float   # mm
    step_y: float   # mm
    integration_time: float = 0.1  # seconds
    model_id: str = "default"
    overlap_percent: float = 0.0  # 0-100%
    serpentine: bool = True  # Use serpentine scanning pattern
    batch_size: int = 1  # Number of spectra to process in batch

@dataclass
class ScanPoint:
    """Single scan point data"""
    x: float
    y: float
    wavelengths: Optional[np.ndarray] = None
    intensities: Optional[np.ndarray] = None
    purity_score: Optional[float] = None
    confidence: Optional[float] = None
    timestamp: Optional[float] = None
    error: Optional[str] = None

@dataclass
class ScanResult:
    """Complete scan result"""
    parameters: ScanParameters
    grid: np.ndarray  # 2D array of purity scores
    x_positions: List[float]
    y_positions: List[float]
    points: List[ScanPoint]
    status: ScanStatus
    start_time: float
    end_time: Optional[float] = None
    total_points: int = 0
    completed_points: int = 0
    error_message: Optional[str] = None

class ScanOrchestrator:
    """
    Orchestrates 2D scanning by coordinating stage movement, spectrum acquisition,
    and ML inference to generate purity maps.
    """
    
    def __init__(self, 
                 stage: StageController, 
                 spectrometer: SpectrometerController,
                 inference_engine: Optional[InferenceEngine] = None,
                 max_workers: int = 2):
        self.stage = stage
        self.spectrometer = spectrometer
        self.inference_engine = inference_engine or InferenceEngine()
        self.preprocessor = SpectrumPreprocessor()
        
        # Scan state
        self.current_scan: Optional[ScanResult] = None
        self.status = ScanStatus.IDLE
        self.cancel_requested = False
        self.pause_requested = False
        
        # Threading for async operations
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Callbacks for progress updates
        self.progress_callbacks: List[Callable[[ScanResult], None]] = []
    
    def add_progress_callback(self, callback: Callable[[ScanResult], None]):
        """Add callback function to receive scan progress updates"""
        self.progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable[[ScanResult], None]):
        """Remove progress callback"""
        if callback in self.progress_callbacks:
            self.progress_callbacks.remove(callback)
    
    def _notify_progress(self):
        """Notify all progress callbacks"""
        if self.current_scan:
            for callback in self.progress_callbacks:
                try:
                    callback(self.current_scan)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
    
    async def start_scan(self, parameters: ScanParameters) -> ScanResult:
        """
        Start a new 2D scan
        
        Args:
            parameters: Scan configuration
            
        Returns:
            ScanResult object that will be updated during scan
        """
        if self.status != ScanStatus.IDLE:
            raise RuntimeError(f"Cannot start scan: current status is {self.status}")
        
        # Validate parameters
        self._validate_scan_parameters(parameters)
        
        # Calculate scan grid
        x_positions = np.arange(parameters.x_start, parameters.x_end + 1e-9, parameters.step_x)
        y_positions = np.arange(parameters.y_start, parameters.y_end + 1e-9, parameters.step_y)
        
        nx, ny = len(x_positions), len(y_positions)
        total_points = nx * ny
        
        logger.info(f"Starting scan: {nx} x {ny} grid ({total_points} points)")
        logger.info(f"Scan area: ({parameters.x_start}, {parameters.y_start}) to ({parameters.x_end}, {parameters.y_end})")
        logger.info(f"Step size: {parameters.step_x} x {parameters.step_y} mm")
        
        # Initialize scan result
        self.current_scan = ScanResult(
            parameters=parameters,
            grid=np.full((ny, nx), np.nan, dtype=float),
            x_positions=x_positions.tolist(),
            y_positions=y_positions.tolist(),
            points=[],
            status=ScanStatus.RUNNING,
            start_time=time.time(),
            total_points=total_points,
            completed_points=0
        )
        
        self.status = ScanStatus.RUNNING
        self.cancel_requested = False
        self.pause_requested = False
        
        try:
            # Ensure hardware is ready
            await self._prepare_hardware()
            
            # Execute scan
            await self._execute_scan(x_positions, y_positions)
            
            # Finalize results
            self.current_scan.status = ScanStatus.COMPLETED
            self.current_scan.end_time = time.time()
            self.status = ScanStatus.IDLE
            
            logger.info(f"✅ Scan completed in {self.current_scan.end_time - self.current_scan.start_time:.1f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            self.current_scan.status = ScanStatus.ERROR
            self.current_scan.error_message = str(e)
            self.current_scan.end_time = time.time()
            self.status = ScanStatus.IDLE
            raise
        
        finally:
            self._notify_progress()
        
        return self.current_scan
    
    async def pause_scan(self):
        """Pause the current scan"""
        if self.status == ScanStatus.RUNNING:
            logger.info("Pausing scan...")
            self.pause_requested = True
            self.status = ScanStatus.PAUSED
    
    async def resume_scan(self):
        """Resume a paused scan"""
        if self.status == ScanStatus.PAUSED:
            logger.info("Resuming scan...")
            self.pause_requested = False
            self.status = ScanStatus.RUNNING
    
    async def cancel_scan(self):
        """Cancel the current scan"""
        if self.status in [ScanStatus.RUNNING, ScanStatus.PAUSED]:
            logger.info("Cancelling scan...")
            self.cancel_requested = True
            if self.current_scan:
                self.current_scan.status = ScanStatus.CANCELLED
                self.current_scan.end_time = time.time()
            self.status = ScanStatus.IDLE
    
    def get_scan_status(self) -> Dict[str, Any]:
        """Get current scan status"""
        if self.current_scan is None:
            return {"status": self.status.value}
        
        progress = self.current_scan.completed_points / self.current_scan.total_points if self.current_scan.total_points > 0 else 0
        elapsed_time = time.time() - self.current_scan.start_time
        
        return {
            "status": self.status.value,
            "progress": progress,
            "completed_points": self.current_scan.completed_points,
            "total_points": self.current_scan.total_points,
            "elapsed_time": elapsed_time,
            "estimated_remaining": (elapsed_time / max(progress, 0.001)) * (1 - progress) if progress > 0 else None,
            "error_message": self.current_scan.error_message
        }
    
    def get_current_result(self) -> Optional[ScanResult]:
        """Get current scan result (may be incomplete)"""
        return self.current_scan
    
    async def _prepare_hardware(self):
        """Ensure hardware is ready for scanning"""
        # Check stage connection and homing
        if not self.stage.is_connected:
            raise RuntimeError("Stage not connected")
        if not self.stage.is_homed:
            logger.info("Homing stage...")
            self.stage.home()
        
        # Check spectrometer connection
        if not self.spectrometer.is_connected:
            raise RuntimeError("Spectrometer not connected")
        
        # Set integration time
        self.spectrometer.set_integration_time(self.current_scan.parameters.integration_time)
        
        logger.info("✅ Hardware ready for scanning")
    
    async def _execute_scan(self, x_positions: np.ndarray, y_positions: np.ndarray):
        """Execute the actual scanning process"""
        nx, ny = len(x_positions), len(y_positions)
        
        # Batch processing setup
        batch_size = self.current_scan.parameters.batch_size
        batch_points = []
        
        for yi, y in enumerate(y_positions):
            # Check for cancellation or pause
            while self.pause_requested and not self.cancel_requested:
                await asyncio.sleep(0.1)
            
            if self.cancel_requested:
                logger.info("Scan cancelled by user")
                break
            
            # Serpentine pattern: reverse X direction on odd rows
            if self.current_scan.parameters.serpentine and yi % 2 == 1:
                x_iter = list(enumerate(x_positions[::-1]))
            else:
                x_iter = list(enumerate(x_positions))
            
            for xi, x in x_iter:
                # Map to correct grid column index
                col = xi if not (self.current_scan.parameters.serpentine and yi % 2 == 1) else (nx - 1 - xi)
                
                try:
                    # Move stage to position
                    self.stage.move_abs(x, y, wait=True)
                    
                    # Small settling delay
                    await asyncio.sleep(0.05)
                    
                    # Read spectrum
                    wavelengths, intensities = self.spectrometer.read_spectrum(
                        self.current_scan.parameters.integration_time
                    )
                    
                    # Create scan point
                    point = ScanPoint(
                        x=x, y=y,
                        wavelengths=wavelengths,
                        intensities=intensities,
                        timestamp=time.time()
                    )
                    
                    # Add to batch or process immediately
                    batch_points.append((point, yi, col))
                    
                    if len(batch_points) >= batch_size or (yi == ny - 1 and xi == len(x_iter) - 1):
                        # Process batch
                        await self._process_batch(batch_points)
                        batch_points = []
                    
                    self.current_scan.completed_points += 1
                    
                    # Periodic progress updates
                    if self.current_scan.completed_points % max(1, self.current_scan.total_points // 20) == 0:
                        self._notify_progress()
                
                except Exception as e:
                    logger.error(f"Error at point ({x:.2f}, {y:.2f}): {e}")
                    # Create error point
                    error_point = ScanPoint(x=x, y=y, error=str(e), timestamp=time.time())
                    self.current_scan.points.append(error_point)
                    self.current_scan.grid[yi, col] = np.nan
                    self.current_scan.completed_points += 1
            
            logger.debug(f"Completed row {yi + 1}/{ny}")
    
    async def _process_batch(self, batch_points: List[Tuple[ScanPoint, int, int]]):
        """Process a batch of scan points through ML inference"""
        if not batch_points:
            return
        
        try:
            # Extract spectra for batch processing
            spectra = []
            for point, _, _ in batch_points:
                if point.wavelengths is not None and point.intensities is not None:
                    # Preprocess spectrum
                    processed = self.preprocessor.preprocess_full(
                        point.wavelengths.tolist(), 
                        point.intensities.tolist()
                    )
                    spectra.append(processed)
                else:
                    spectra.append(None)
            
            # Run inference (batch or individual)
            if len(spectra) == 1 and spectra[0] is not None:
                # Single spectrum
                result = await self.inference_engine.predict(
                    batch_points[0][0].wavelengths.tolist(),
                    batch_points[0][0].intensities.tolist()
                )
                purity_scores = [result.get("purity_percentage", np.nan)]
                confidences = [result.get("confidence_score", np.nan)]
            else:
                # For now, process individually (can be optimized for true batch processing)
                purity_scores = []
                confidences = []
                for spectrum in spectra:
                    if spectrum is not None:
                        # Convert back to wavelengths/intensities for existing API
                        point_data = batch_points[len(purity_scores)][0]
                        result = await self.inference_engine.predict(
                            point_data.wavelengths.tolist(),
                            point_data.intensities.tolist()
                        )
                        purity_scores.append(result.get("purity_percentage", np.nan))
                        confidences.append(result.get("confidence_score", np.nan))
                    else:
                        purity_scores.append(np.nan)
                        confidences.append(np.nan)
            
            # Update results
            for i, (point, yi, col) in enumerate(batch_points):
                point.purity_score = purity_scores[i]
                point.confidence = confidences[i]
                
                # Update grid
                self.current_scan.grid[yi, col] = purity_scores[i]
                
                # Store point
                self.current_scan.points.append(point)
        
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            # Mark all points in batch as errors
            for point, yi, col in batch_points:
                point.error = str(e)
                self.current_scan.grid[yi, col] = np.nan
                self.current_scan.points.append(point)
    
    def _validate_scan_parameters(self, params: ScanParameters):
        """Validate scan parameters"""
        if params.x_start >= params.x_end:
            raise ValueError("x_start must be less than x_end")
        if params.y_start >= params.y_end:
            raise ValueError("y_start must be less than y_end")
        if params.step_x <= 0 or params.step_y <= 0:
            raise ValueError("Step sizes must be positive")
        if params.integration_time <= 0:
            raise ValueError("Integration time must be positive")
        if not (0 <= params.overlap_percent <= 100):
            raise ValueError("Overlap percent must be between 0 and 100")
        
        # Check stage limits
        x_limits, y_limits = self.stage.get_limits()
        if not (x_limits[0] <= params.x_start <= x_limits[1] and x_limits[0] <= params.x_end <= x_limits[1]):
            raise ValueError(f"X range [{params.x_start}, {params.x_end}] outside stage limits {x_limits}")
        if not (y_limits[0] <= params.y_start <= y_limits[1] and y_limits[0] <= params.y_end <= y_limits[1]):
            raise ValueError(f"Y range [{params.y_start}, {params.y_end}] outside stage limits {y_limits}")
    
    def export_scan_data(self, filepath: str, format: str = "json"):
        """
        Export scan data to file
        
        Args:
            filepath: Output file path
            format: Export format ("json", "csv", "hdf5")
        """
        if self.current_scan is None:
            raise RuntimeError("No scan data to export")
        
        if format.lower() == "json":
            import json
            
            # Convert numpy arrays to lists for JSON serialization
            export_data = {
                "parameters": asdict(self.current_scan.parameters),
                "grid": self.current_scan.grid.tolist(),
                "x_positions": self.current_scan.x_positions,
                "y_positions": self.current_scan.y_positions,
                "status": self.current_scan.status.value,
                "start_time": self.current_scan.start_time,
                "end_time": self.current_scan.end_time,
                "total_points": self.current_scan.total_points,
                "completed_points": self.current_scan.completed_points,
                "points": [
                    {
                        "x": p.x, "y": p.y,
                        "purity_score": p.purity_score,
                        "confidence": p.confidence,
                        "timestamp": p.timestamp,
                        "error": p.error
                    }
                    for p in self.current_scan.points
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        elif format.lower() == "csv":
            import pandas as pd
            
            # Create DataFrame from scan points
            data = []
            for point in self.current_scan.points:
                data.append({
                    "x_mm": point.x,
                    "y_mm": point.y,
                    "purity_score": point.purity_score,
                    "confidence": point.confidence,
                    "timestamp": point.timestamp,
                    "error": point.error
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Scan data exported to {filepath}")
