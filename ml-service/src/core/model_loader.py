import torch
import joblib
import json
import time
import numpy as np
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
            
            # Warmup model
            await self._warmup_model()
            
            logger.info("✅ Baseline model loaded and warmed up successfully")
            
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
            
            # Warmup model
            await self._warmup_model()
            
            logger.info("✅ PLSR model loaded and warmed up successfully")
            
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
    
    async def _warmup_model(self):
        """
        Warm up the model with dummy predictions to reduce first-inference latency
        """
        try:
            logger.info("Warming up model...")
            start_time = time.time()
            
            # Generate dummy spectrum data (typical Raman spectrum size)
            dummy_spectrum = np.random.rand(1024).astype(np.float32)
            
            if self._model_type == "baseline":
                # Warmup PyTorch model
                with torch.no_grad():
                    dummy_tensor = torch.FloatTensor(dummy_spectrum).unsqueeze(0)
                    if settings.DEVICE == "cuda" and torch.cuda.is_available():
                        dummy_tensor = dummy_tensor.cuda()
                        self._model = self._model.cuda()
                    
                    # Run several warmup predictions
                    for _ in range(3):
                        _ = self._model(dummy_tensor)
                    
                    # Synchronize if using CUDA
                    if settings.DEVICE == "cuda" and torch.cuda.is_available():
                        torch.cuda.synchronize()
            
            elif self._model_type == "plsr":
                # Warmup PLSR model
                regressor = self._model["regressor"]
                scaler = self._model.get("scaler")
                
                dummy_input = dummy_spectrum.reshape(1, -1)
                if scaler:
                    dummy_input = scaler.transform(dummy_input)
                
                # Run several warmup predictions
                for _ in range(3):
                    _ = regressor.predict(dummy_input)
            
            elif self._model_type == "mock":
                # Mock warmup (just simulate some computation)
                for _ in range(3):
                    _ = np.mean(dummy_spectrum) + np.std(dummy_spectrum)
            
            warmup_time = time.time() - start_time
            logger.info(f"Model warmup completed in {warmup_time:.3f} seconds")
            
        except Exception as e:
            logger.warning(f"Model warmup failed (non-critical): {e}")
    
    @classmethod
    def optimize_for_inference(cls):
        """
        Apply inference optimizations to the loaded model
        """
        instance = cls()
        
        if instance._model is None:
            logger.warning("No model loaded for optimization")
            return
        
        try:
            if instance._model_type == "baseline" and isinstance(instance._model, torch.nn.Module):
                logger.info("Optimizing PyTorch model for inference...")
                
                # Set to evaluation mode
                instance._model.eval()
                
                # Disable gradient computation globally for inference
                torch.set_grad_enabled(False)
                
                # Try to optimize with TorchScript (if supported)
                try:
                    dummy_input = torch.randn(1, 1024)  # Adjust size as needed
                    if settings.DEVICE == "cuda" and torch.cuda.is_available():
                        dummy_input = dummy_input.cuda()
                    
                    # Trace the model
                    traced_model = torch.jit.trace(instance._model, dummy_input)
                    traced_model.eval()
                    
                    # Replace model with traced version
                    instance._model = traced_model
                    logger.info("✅ Model optimized with TorchScript")
                    
                except Exception as e:
                    logger.warning(f"TorchScript optimization failed: {e}")
                
                # Set optimal number of threads for CPU inference
                if settings.DEVICE == "cpu":
                    torch.set_num_threads(min(4, torch.get_num_threads()))
            
            logger.info("Model optimization completed")
            
        except Exception as e:
            logger.error(f"Model optimization failed: {e}")
    
    @classmethod
    def get_performance_stats(cls) -> Dict[str, Any]:
        """
        Get performance statistics for the loaded model
        """
        instance = cls()
        
        if instance._model is None:
            return {"error": "No model loaded"}
        
        try:
            stats = {
                "model_type": instance._model_type,
                "device": str(settings.DEVICE),
                "model_info": instance._model_info or {}
            }
            
            if instance._model_type == "baseline":
                # PyTorch model stats
                if hasattr(instance._model, 'parameters'):
                    total_params = sum(p.numel() for p in instance._model.parameters())
                    trainable_params = sum(p.numel() for p in instance._model.parameters() if p.requires_grad)
                    stats.update({
                        "total_parameters": total_params,
                        "trainable_parameters": trainable_params,
                        "model_size_mb": total_params * 4 / (1024 * 1024),  # Assuming float32
                        "is_traced": hasattr(instance._model, '_c'),  # TorchScript indicator
                    })
                
                if torch.cuda.is_available():
                    stats.update({
                        "cuda_available": True,
                        "cuda_device_count": torch.cuda.device_count(),
                        "current_device": torch.cuda.current_device() if settings.DEVICE == "cuda" else None
                    })
            
            elif instance._model_type == "plsr":
                # PLSR model stats
                regressor = instance._model["regressor"]
                stats.update({
                    "n_components": getattr(regressor, 'n_components', None),
                    "has_scaler": instance._model.get("scaler") is not None
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {"error": str(e)}
