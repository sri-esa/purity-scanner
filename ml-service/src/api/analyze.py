from fastapi import APIRouter, HTTPException
from src.api.models import SpectrumData, PurityResult, ErrorResponse, ModelInfo
from src.core.inference import InferenceEngine
from src.core.model_loader import ModelLoader
from config import settings
import time
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=PurityResult)
async def analyze_spectrum(spectrum: SpectrumData):
    """
    Analyze Raman spectrum for purity determination
    """
    start_time = time.time()
    
    try:
        # Check if model is loaded
        if not ModelLoader.is_loaded():
            raise HTTPException(
                status_code=503,
                detail="ML model not loaded. Service unavailable."
            )
        
        # Perform inference
        result = await InferenceEngine.predict(
            wavelengths=spectrum.wavelengths,
            intensities=spectrum.intensities
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return PurityResult(
            purity_percentage=result["purity_percentage"],
            confidence_score=result["confidence_score"],
            contaminants=result.get("contaminants"),
            model_used=ModelLoader.get_model_type(),
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during analysis"
        )

@router.get("/models", response_model=List[ModelInfo])
async def get_available_models():
    """
    Get information about available ML models
    """
    try:
        models = ModelLoader.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch model information"
        )

@router.post("/models/{model_name}/load")
async def load_model(model_name: str):
    """
    Load a specific model
    """
    try:
        success = await ModelLoader.load_model(model_name)
        if success:
            return {"message": f"Model {model_name} loaded successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to load model {model_name}"
            )
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error loading model {model_name}"
        )
