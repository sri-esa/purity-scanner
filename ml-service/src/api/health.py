from fastapi import APIRouter
from src.api.models import HealthResponse
from src.core.model_loader import ModelLoader
from config import settings
import time

router = APIRouter()

# Track startup time
startup_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for the ML service
    """
    current_time = time.time()
    uptime = current_time - startup_time
    
    model_loaded = ModelLoader.is_loaded()
    model_type = ModelLoader.get_model_type() if model_loaded else "none"
    
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        model_type=model_type,
        uptime_seconds=uptime
    )

@router.get("/status")
async def status():
    """
    Simple status endpoint
    """
    return {
        "service": "PurityScan ML Service",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }
