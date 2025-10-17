# src/api/scan.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import logging
import io
import json
import numpy as np
from datetime import datetime

from src.core.scan_orchestrator import ScanOrchestrator, ScanParameters, ScanStatus
from src.hardware.stage_controller import StageController, StageConfig
from src.hardware.spectrometer import SpectrometerController, SpectrometerConfig
from src.core.inference import InferenceEngine
from src.visualization.map_generator import MapGenerator, HeatmapConfig

logger = logging.getLogger(__name__)

# Pydantic models for API
class ScanRequest(BaseModel):
    x_start: float = Field(..., description="Start X position in mm", ge=0)
    y_start: float = Field(..., description="Start Y position in mm", ge=0)
    x_end: float = Field(..., description="End X position in mm", gt=0)
    y_end: float = Field(..., description="End Y position in mm", gt=0)
    step_x: float = Field(0.5, description="X step size in mm", gt=0)
    step_y: float = Field(0.5, description="Y step size in mm", gt=0)
    integration_time: float = Field(0.1, description="Integration time in seconds", gt=0, le=10)
    model_id: str = Field("default", description="Model ID to use for inference")
    overlap_percent: float = Field(0.0, description="Overlap percentage", ge=0, le=100)
    serpentine: bool = Field(True, description="Use serpentine scanning pattern")
    batch_size: int = Field(1, description="Batch size for inference", ge=1, le=10)

class ScanStatusResponse(BaseModel):
    status: str
    progress: float = Field(0.0, description="Progress as fraction (0-1)")
    completed_points: int = 0
    total_points: int = 0
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None
    error_message: Optional[str] = None

class ScanResultSummary(BaseModel):
    scan_id: str
    status: str
    parameters: Dict[str, Any]
    grid_shape: List[int]
    statistics: Dict[str, float]
    start_time: float
    end_time: Optional[float] = None
    total_points: int
    completed_points: int

# Global scan orchestrator instance
_scan_orchestrator: Optional[ScanOrchestrator] = None
_current_scan_id: Optional[str] = None

def get_scan_orchestrator() -> ScanOrchestrator:
    """Get or create scan orchestrator instance"""
    global _scan_orchestrator
    
    if _scan_orchestrator is None:
        # Initialize hardware controllers
        stage_config = StageConfig(x_max_mm=50.0, y_max_mm=50.0)
        stage = StageController(stage_config)
        
        spec_config = SpectrometerConfig()
        spectrometer = SpectrometerController(spec_config)
        
        # Connect hardware (in production, handle connection errors)
        try:
            stage.connect()
            stage.home()
            spectrometer.connect()
        except Exception as e:
            logger.warning(f"Hardware connection failed (using mock): {e}")
        
        # Create orchestrator
        _scan_orchestrator = ScanOrchestrator(
            stage=stage,
            spectrometer=spectrometer,
            inference_engine=InferenceEngine(),
            max_workers=2
        )
    
    return _scan_orchestrator

# Create router
router = APIRouter()

@router.post("/start", response_model=Dict[str, str])
async def start_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start a new 2D purity scan
    
    Args:
        scan_request: Scan parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        Scan ID and status
    """
    global _current_scan_id
    
    try:
        orchestrator = get_scan_orchestrator()
        
        # Check if scan is already running
        if orchestrator.status != ScanStatus.IDLE:
            raise HTTPException(
                status_code=409,
                detail=f"Scan already in progress (status: {orchestrator.status.value})"
            )
        
        # Convert request to scan parameters
        scan_params = ScanParameters(
            x_start=scan_request.x_start,
            y_start=scan_request.y_start,
            x_end=scan_request.x_end,
            y_end=scan_request.y_end,
            step_x=scan_request.step_x,
            step_y=scan_request.step_y,
            integration_time=scan_request.integration_time,
            model_id=scan_request.model_id,
            overlap_percent=scan_request.overlap_percent,
            serpentine=scan_request.serpentine,
            batch_size=scan_request.batch_size
        )
        
        # Generate scan ID
        _current_scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start scan in background
        async def run_scan():
            try:
                await orchestrator.start_scan(scan_params)
                logger.info(f"Scan {_current_scan_id} completed successfully")
            except Exception as e:
                logger.error(f"Scan {_current_scan_id} failed: {e}")
        
        background_tasks.add_task(run_scan)
        
        return {
            "scan_id": _current_scan_id,
            "status": "started",
            "message": "Scan started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scan: {str(e)}")

@router.get("/status", response_model=ScanStatusResponse)
async def get_scan_status():
    """
    Get current scan status and progress
    
    Returns:
        Current scan status information
    """
    try:
        orchestrator = get_scan_orchestrator()
        status_data = orchestrator.get_scan_status()
        
        return ScanStatusResponse(**status_data)
        
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scan status: {str(e)}")

@router.post("/pause")
async def pause_scan():
    """
    Pause the current scan
    
    Returns:
        Success message
    """
    try:
        orchestrator = get_scan_orchestrator()
        
        if orchestrator.status != ScanStatus.RUNNING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pause scan: current status is {orchestrator.status.value}"
            )
        
        await orchestrator.pause_scan()
        
        return {"message": "Scan paused successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pause scan: {str(e)}")

@router.post("/resume")
async def resume_scan():
    """
    Resume a paused scan
    
    Returns:
        Success message
    """
    try:
        orchestrator = get_scan_orchestrator()
        
        if orchestrator.status != ScanStatus.PAUSED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot resume scan: current status is {orchestrator.status.value}"
            )
        
        await orchestrator.resume_scan()
        
        return {"message": "Scan resumed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resume scan: {str(e)}")

@router.post("/cancel")
async def cancel_scan():
    """
    Cancel the current scan
    
    Returns:
        Success message
    """
    try:
        orchestrator = get_scan_orchestrator()
        
        if orchestrator.status not in [ScanStatus.RUNNING, ScanStatus.PAUSED]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel scan: current status is {orchestrator.status.value}"
            )
        
        await orchestrator.cancel_scan()
        
        return {"message": "Scan cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel scan: {str(e)}")

@router.get("/result/summary", response_model=ScanResultSummary)
async def get_scan_result_summary():
    """
    Get summary of current/last scan result
    
    Returns:
        Scan result summary
    """
    try:
        orchestrator = get_scan_orchestrator()
        result = orchestrator.get_current_result()
        
        if result is None:
            raise HTTPException(status_code=404, detail="No scan result available")
        
        # Calculate statistics
        valid_data = result.grid[~np.isnan(result.grid)] if result.grid.size > 0 else []
        
        if len(valid_data) > 0:
            import numpy as np
            statistics = {
                "mean": float(np.mean(valid_data)),
                "std": float(np.std(valid_data)),
                "min": float(np.min(valid_data)),
                "max": float(np.max(valid_data)),
                "median": float(np.median(valid_data)),
                "valid_points": len(valid_data)
            }
        else:
            statistics = {
                "mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "median": 0.0, "valid_points": 0
            }
        
        return ScanResultSummary(
            scan_id=_current_scan_id or "unknown",
            status=result.status.value,
            parameters=result.parameters.__dict__,
            grid_shape=list(result.grid.shape),
            statistics=statistics,
            start_time=result.start_time,
            end_time=result.end_time,
            total_points=result.total_points,
            completed_points=result.completed_points
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan result summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scan result: {str(e)}")

@router.get("/result/heatmap")
async def get_scan_heatmap(
    format: str = "png",
    colormap: str = "viridis",
    interpolation: str = "nearest",
    width: int = 800,
    height: int = 600
):
    """
    Get heatmap visualization of scan result
    
    Args:
        format: Image format (png, jpg)
        colormap: Matplotlib colormap name
        interpolation: Interpolation method
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Heatmap image
    """
    try:
        orchestrator = get_scan_orchestrator()
        result = orchestrator.get_current_result()
        
        if result is None or result.grid.size == 0:
            raise HTTPException(status_code=404, detail="No scan result available")
        
        # Create heatmap configuration
        config = HeatmapConfig(
            figsize=(width/100, height/100),  # Convert pixels to inches (approx)
            cmap=colormap,
            interpolation=interpolation,
            title=f"Purity Scan - {_current_scan_id or 'Unknown'}"
        )
        
        # Generate heatmap
        generator = MapGenerator(config)
        
        import numpy as np
        x_pos = np.array(result.x_positions) if result.x_positions else None
        y_pos = np.array(result.y_positions) if result.y_positions else None
        
        image_bytes = generator.generate_heatmap(
            result.grid,
            x_positions=x_pos,
            y_positions=y_pos,
            return_bytes=True
        )
        
        # Return image response
        media_type = f"image/{format.lower()}"
        return Response(content=image_bytes, media_type=media_type)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate heatmap: {str(e)}")

@router.get("/result/data")
async def get_scan_data(format: str = "json"):
    """
    Get raw scan data in specified format
    
    Args:
        format: Data format (json, csv)
        
    Returns:
        Scan data in requested format
    """
    try:
        orchestrator = get_scan_orchestrator()
        result = orchestrator.get_current_result()
        
        if result is None:
            raise HTTPException(status_code=404, detail="No scan result available")
        
        if format.lower() == "json":
            # Return JSON data
            import numpy as np
            
            data = {
                "scan_id": _current_scan_id or "unknown",
                "parameters": result.parameters.__dict__,
                "grid": result.grid.tolist(),
                "x_positions": result.x_positions,
                "y_positions": result.y_positions,
                "status": result.status.value,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "total_points": result.total_points,
                "completed_points": result.completed_points,
                "points": [
                    {
                        "x": p.x, "y": p.y,
                        "purity_score": p.purity_score,
                        "confidence": p.confidence,
                        "timestamp": p.timestamp,
                        "error": p.error
                    }
                    for p in result.points
                ]
            }
            
            return data
            
        elif format.lower() == "csv":
            # Return CSV data
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["x_mm", "y_mm", "purity_percent", "confidence", "timestamp", "error"])
            
            # Write data points
            for point in result.points:
                writer.writerow([
                    point.x, point.y, point.purity_score, 
                    point.confidence, point.timestamp, point.error
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=scan_data_{_current_scan_id or 'unknown'}.csv"}
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scan data: {str(e)}")

@router.get("/hardware/status")
async def get_hardware_status():
    """
    Get status of hardware components
    
    Returns:
        Hardware status information
    """
    try:
        orchestrator = get_scan_orchestrator()
        
        # Get stage status
        stage_pos = orchestrator.stage.get_position()
        stage_limits = orchestrator.stage.get_limits()
        
        # Get spectrometer status
        spec_status = orchestrator.spectrometer.get_status()
        
        return {
            "stage": {
                "connected": orchestrator.stage.is_connected,
                "homed": orchestrator.stage.is_homed,
                "position": {"x": stage_pos[0], "y": stage_pos[1]},
                "limits": {
                    "x_range": stage_limits[0],
                    "y_range": stage_limits[1]
                },
                "emergency_stop": orchestrator.stage.emergency_stop
            },
            "spectrometer": spec_status,
            "scan_orchestrator": {
                "status": orchestrator.status.value,
                "active_scan": orchestrator.current_scan is not None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting hardware status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hardware status: {str(e)}")

@router.post("/hardware/home")
async def home_stage():
    """
    Home the motorized stage
    
    Returns:
        Success message and new position
    """
    try:
        orchestrator = get_scan_orchestrator()
        
        if orchestrator.status == ScanStatus.RUNNING:
            raise HTTPException(
                status_code=409,
                detail="Cannot home stage while scan is running"
            )
        
        position = orchestrator.stage.home()
        
        return {
            "message": "Stage homed successfully",
            "position": {"x": position[0], "y": position[1]}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error homing stage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to home stage: {str(e)}")

@router.post("/hardware/emergency_stop")
async def emergency_stop():
    """
    Activate emergency stop for all hardware
    
    Returns:
        Success message
    """
    try:
        orchestrator = get_scan_orchestrator()
        
        # Stop stage
        orchestrator.stage.stop()
        
        # Cancel any running scan
        if orchestrator.status in [ScanStatus.RUNNING, ScanStatus.PAUSED]:
            await orchestrator.cancel_scan()
        
        return {"message": "Emergency stop activated"}
        
    except Exception as e:
        logger.error(f"Error in emergency stop: {e}")
        raise HTTPException(status_code=500, detail=f"Emergency stop failed: {str(e)}")

@router.post("/hardware/reset_emergency")
async def reset_emergency_stop():
    """
    Reset emergency stop condition
    
    Returns:
        Success message
    """
    try:
        orchestrator = get_scan_orchestrator()
        orchestrator.stage.reset_emergency_stop()
        
        return {"message": "Emergency stop reset"}
        
    except Exception as e:
        logger.error(f"Error resetting emergency stop: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset emergency stop: {str(e)}")
