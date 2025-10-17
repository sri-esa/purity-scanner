from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.health import router as health_router
from src.api.analyze import router as analyze_router
from src.core.model_loader import ModelLoader
from config import settings
import logging

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="PurityScan ML Service",
    description="Machine Learning microservice for Raman spectroscopy analysis",
    version="1.0.0"
)

# CORS - Allow your Node.js backend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your backend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/ml", tags=["health"])
app.include_router(analyze_router, prefix="/api/ml", tags=["analysis"])

@app.on_event("startup")
async def startup_event():
    """Load ML model on startup"""
    logger.info("🚀 Starting ML Service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Device: {settings.DEVICE}")
    
    # Load model
    try:
        await ModelLoader.initialize()
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        # Don't fail startup, but log the error

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down ML Service...")

@app.get("/")
async def root():
    return {
        "service": "PurityScan ML Service",
        "version": "1.0.0",
        "status": "running"
    }
