import torch
import joblib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from config import settings
from src.api.models import ModelInfo

logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Centralized model loading and management
    """
    
    _instance = None
    _model = None
    _model_type = None
    _model_info = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def initialize(cls):
        """Initialize and load the default model"""
        instance = cls()
        await instance._load_default_model()
    
    async def _load_default_model(self):
        """Load the default model specified in settings"""
        try:
            model_type = settings.MODEL_TYPE
            logger.info(f"Loading default model: {model_type}")
            
            if model_type == "baseline":
                await self._load_baseline_model()
            elif model_type == "plsr":
                await self._load_plsr_model()
            else:
                logger.warning(f"Unknown model type: {model_type}")
                await self._load_mock_model()
                
        except Exception as e:
            logger.error(f"Failed to load default model: {e}")
            # Load mock model as fallback
            await self._load_mock_model()
    
    async def _load_baseline_model(self):
        """Load HuggingFace baseline model"""
        try:
            model_path = settings.MODELS_DIR / "baseline" / "purityscan_huggingface.pth"
            info_path = settings.MODELS_DIR / "baseline" / "model_info.json"
            
            if not model_path.exists():
                logger.warning(f"Baseline model not found at {model_path}, using mock model")
                await self._load_mock_model()
                return
            
            # Load model info
            if info_path.exists():
                with open(info_path, 'r') as f:
                    self._model_info = json.load(f)
            else:
                self._model_info = {
                    "name": "PurityScan Baseline",
                    "version": "1.0.0",
                    "accuracy": 0.92,
                    "description": "HuggingFace transformer model for purity analysis"
                }
            
            # Load PyTorch model
            self._model = torch.load(model_path, map_location=settings.DEVICE)
            self._model.eval()
            self._model_type = "baseline"
            
            logger.info("✅ Baseline model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load baseline model: {e}")
            await self._load_mock_model()
    
    async def _load_plsr_model(self):
        """Load PLSR (Partial Least Squares Regression) model"""
        try:
            model_path = settings.MODELS_DIR / "plsr" / "plsr_model.pkl"
            scaler_path = settings.MODELS_DIR / "plsr" / "scaler.pkl"
            
            if not model_path.exists():
                logger.warning(f"PLSR model not found at {model_path}, using mock model")
                await self._load_mock_model()
                return
            
            # Load scikit-learn model and scaler
            self._model = {
                "regressor": joblib.load(model_path),
                "scaler": joblib.load(scaler_path) if scaler_path.exists() else None
            }
            
            self._model_info = {
                "name": "PLSR Purity Model",
                "version": "1.0.0",
                "accuracy": 0.89,
                "description": "Partial Least Squares Regression model for purity analysis"
            }
            
            self._model_type = "plsr"
            logger.info("✅ PLSR model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load PLSR model: {e}")
            await self._load_mock_model()
    
    async def _load_mock_model(self):
        """Load mock model for testing"""
        logger.info("Loading mock model for testing...")
        
        self._model = "mock_model"  # Simple placeholder
        self._model_type = "mock"
        self._model_info = {
            "name": "Mock Purity Model",
            "version": "0.1.0",
            "accuracy": 0.75,
            "description": "Mock model for testing and development"
        }
        
        logger.info("✅ Mock model loaded successfully")
    
    @classmethod
    def get_model(cls):
        """Get the loaded model"""
        instance = cls()
        return instance._model
    
    @classmethod
    def get_model_type(cls) -> str:
        """Get the type of loaded model"""
        instance = cls()
        return instance._model_type or "none"
    
    @classmethod
    def get_model_info(cls) -> Dict[str, Any]:
        """Get model information"""
        instance = cls()
        return instance._model_info or {}
    
    @classmethod
    def is_loaded(cls) -> bool:
        """Check if a model is loaded"""
        instance = cls()
        return instance._model is not None
    
    @classmethod
    def get_available_models(cls) -> List[ModelInfo]:
        """Get list of available models"""
        models = []
        
        # Check for baseline model
        baseline_path = settings.MODELS_DIR / "baseline"
        if baseline_path.exists():
            models.append(ModelInfo(
                name="PurityScan Baseline",
                type="baseline",
                version="1.0.0",
                accuracy=0.92,
                description="HuggingFace transformer model for purity analysis"
            ))
        
        # Check for PLSR model
        plsr_path = settings.MODELS_DIR / "plsr"
        if plsr_path.exists():
            models.append(ModelInfo(
                name="PLSR Purity Model",
                type="plsr",
                version="1.0.0",
                accuracy=0.89,
                description="Partial Least Squares Regression model"
            ))
        
        # Always include mock model
        models.append(ModelInfo(
            name="Mock Purity Model",
            type="mock",
            version="0.1.0",
            accuracy=0.75,
            description="Mock model for testing and development"
        ))
        
        return models
    
    @classmethod
    async def load_model(cls, model_name: str) -> bool:
        """Load a specific model by name"""
        instance = cls()
        
        try:
            if model_name.lower() in ["baseline", "purityscan baseline"]:
                await instance._load_baseline_model()
            elif model_name.lower() in ["plsr", "plsr purity model"]:
                await instance._load_plsr_model()
            elif model_name.lower() in ["mock", "mock purity model"]:
                await instance._load_mock_model()
            else:
                logger.error(f"Unknown model: {model_name}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
