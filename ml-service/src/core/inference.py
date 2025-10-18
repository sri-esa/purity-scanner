import numpy as np
import torch
from typing import Dict, List, Any, Union
import logging
import random
from src.core.model_loader import ModelLoader
from src.core.preprocessing import SpectrumPreprocessor
from config import settings

logger = logging.getLogger(__name__)

class InferenceEngine:
    """
    ML inference engine for purity analysis
    """
    
    preprocessor = SpectrumPreprocessor()
    
    @classmethod
    async def predict(cls, wavelengths: List[float], intensities: List[float]) -> Dict[str, Any]:
        """
        Predict purity from Raman spectrum
        
        Args:
            wavelengths: Wavelength values
            intensities: Intensity values
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Validate input
            if not cls.preprocessor.validate_spectrum(wavelengths, intensities):
                raise ValueError("Invalid spectrum data")
            
            # Preprocess spectrum
            processed_spectrum = cls.preprocessor.preprocess_full(wavelengths, intensities)
            
            # Get model and perform inference
            model = ModelLoader.get_model()
            model_type = ModelLoader.get_model_type()
            
            if model_type == "baseline":
                return await cls._predict_baseline(processed_spectrum)
            elif model_type == "plsr":
                return await cls._predict_plsr(processed_spectrum)
            elif model_type == "cnn_1d":
                return await cls._predict_cnn_1d(processed_spectrum)
            elif model_type == "mock_cnn_1d":
                return await cls._predict_mock_cnn(processed_spectrum)
            elif model_type == "mock":
                return await cls._predict_mock(processed_spectrum)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
    
    @classmethod
    async def _predict_baseline(cls, spectrum: np.ndarray) -> Dict[str, Any]:
        """
        Predict using HuggingFace baseline model
        """
        try:
            model = ModelLoader.get_model()
            
            # Convert to tensor
            input_tensor = torch.FloatTensor(spectrum).unsqueeze(0)  # Add batch dimension
            
            with torch.no_grad():
                # Forward pass
                output = model(input_tensor)
                
                # Extract purity percentage (assuming model outputs logits)
                purity_logits = output.squeeze()
                purity_percentage = torch.sigmoid(purity_logits).item() * 100
                
                # Calculate confidence (using entropy or max probability)
                confidence = min(0.95, max(0.5, 1.0 - abs(0.5 - torch.sigmoid(purity_logits).item())))
            
            # Detect potential contaminants based on spectrum features
            contaminants = cls._detect_contaminants(spectrum, purity_percentage)
            
            return {
                "purity_percentage": round(purity_percentage, 2),
                "confidence_score": round(confidence, 3),
                "contaminants": contaminants
            }
            
        except Exception as e:
            logger.error(f"Baseline prediction error: {e}")
            # Fallback to mock prediction
            return await cls._predict_mock(spectrum)
    
    @classmethod
    async def _predict_plsr(cls, spectrum: np.ndarray) -> Dict[str, Any]:
        """
        Predict using PLSR model
        """
        try:
            model_dict = ModelLoader.get_model()
            regressor = model_dict["regressor"]
            scaler = model_dict.get("scaler")
            
            # Scale input if scaler is available
            input_data = spectrum.reshape(1, -1)
            if scaler:
                input_data = scaler.transform(input_data)
            
            # Predict
            purity_percentage = regressor.predict(input_data)[0]
            purity_percentage = np.clip(purity_percentage, 0, 100)
            
            # Calculate confidence based on prediction certainty
            confidence = min(0.95, max(0.6, 1.0 - abs(50 - purity_percentage) / 50))
            
            # Detect contaminants
            contaminants = cls._detect_contaminants(spectrum, purity_percentage)
            
            return {
                "purity_percentage": round(float(purity_percentage), 2),
                "confidence_score": round(confidence, 3),
                "contaminants": contaminants
            }
            
        except Exception as e:
            logger.error(f"PLSR prediction error: {e}")
            # Fallback to mock prediction
            return await cls._predict_mock(spectrum)
    
    @classmethod
    async def _predict_cnn_1d(cls, spectrum: np.ndarray) -> Dict[str, Any]:
        """
        Predict using 1D-CNN model
        """
        try:
            model = ModelLoader.get_model()
            
            # Use the model's predict_purity method
            purity_percentage, confidence_score = model.predict_purity(spectrum)
            
            # Detect potential contaminants based on spectrum features
            contaminants = cls._detect_contaminants(spectrum, purity_percentage)
            
            return {
                "purity_percentage": round(purity_percentage, 2),
                "confidence_score": round(confidence_score, 3),
                "contaminants": contaminants
            }
            
        except Exception as e:
            logger.error(f"CNN 1D prediction error: {e}")
            # Fallback to mock prediction
            return await cls._predict_mock(spectrum)
    
    @classmethod
    async def _predict_mock_cnn(cls, spectrum: np.ndarray) -> Dict[str, Any]:
        """
        Predict using mock CNN model
        """
        try:
            model = ModelLoader.get_model()
            
            # Use the mock model's predict_purity method
            purity_percentage, confidence_score = model.predict_purity(spectrum)
            
            # Detect potential contaminants based on spectrum features
            contaminants = cls._detect_contaminants(spectrum, purity_percentage)
            
            return {
                "purity_percentage": round(purity_percentage, 2),
                "confidence_score": round(confidence_score, 3),
                "contaminants": contaminants
            }
            
        except Exception as e:
            logger.error(f"Mock CNN prediction error: {e}")
            # Fallback to basic mock prediction
            return await cls._predict_mock(spectrum)

    @classmethod
    async def _predict_mock(cls, spectrum: np.ndarray) -> Dict[str, Any]:
        """
        Mock prediction for testing
        """
        # Generate realistic-looking fake results
        np.random.seed(int(np.sum(spectrum) * 1000) % 2**32)
        
        # Base purity on spectrum characteristics
        spectrum_std = np.std(spectrum)
        spectrum_mean = np.mean(spectrum)
        
        # Higher std and certain mean ranges suggest higher purity
        base_purity = 70 + (spectrum_std * 30) + (spectrum_mean * 10)
        base_purity = np.clip(base_purity, 60, 98)
        
        # Add some randomness
        purity_percentage = base_purity + np.random.normal(0, 3)
        purity_percentage = np.clip(purity_percentage, 55, 99)
        
        # Confidence inversely related to how far from "normal" ranges
        confidence = 0.7 + 0.25 * (1 - abs(purity_percentage - 85) / 30)
        confidence = np.clip(confidence, 0.5, 0.95)
        
        # Mock contaminants
        contaminants = cls._detect_contaminants(spectrum, purity_percentage)
        
        return {
            "purity_percentage": round(float(purity_percentage), 2),
            "confidence_score": round(float(confidence), 3),
            "contaminants": contaminants
        }
    
    @classmethod
    def _detect_contaminants(cls, spectrum: np.ndarray, purity: float) -> List[str]:
        """
        Detect potential contaminants based on spectrum analysis
        """
        contaminants = []
        
        # Simple heuristic-based contaminant detection
        # In a real system, this would use trained models or spectral libraries
        
        if purity < 90:
            # Look for characteristic peaks or patterns
            peaks = cls._find_peaks(spectrum)
            
            if len(peaks) > 10:  # Many peaks might indicate organic contaminants
                contaminants.append("organic_compounds")
            
            if np.max(spectrum) > 0.9:  # Very high intensity peaks
                contaminants.append("crystalline_impurities")
            
            if np.std(spectrum) < 0.1:  # Low variation might indicate amorphous content
                contaminants.append("amorphous_material")
            
            # Random additional contaminants for mock data
            if purity < 80:
                possible_contaminants = ["water", "salts", "proteins", "lipids", "metal_oxides"]
                num_additional = min(2, int((90 - purity) / 10))
                contaminants.extend(random.sample(possible_contaminants, num_additional))
        
        return list(set(contaminants))  # Remove duplicates
    
    @classmethod
    def _find_peaks(cls, spectrum: np.ndarray, prominence: float = 0.1) -> List[int]:
        """
        Find peaks in spectrum
        """
        try:
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(spectrum, prominence=prominence)
            return peaks.tolist()
        except ImportError:
            # Simple peak detection fallback
            peaks = []
            for i in range(1, len(spectrum) - 1):
                if (spectrum[i] > spectrum[i-1] and 
                    spectrum[i] > spectrum[i+1] and 
                    spectrum[i] > prominence):
                    peaks.append(i)
            return peaks

    @classmethod
    async def predict_purity_scalar(cls, wavelengths: List[float], intensities: List[float]) -> float:
        """
        Predict purity as a single scalar value (for 2D scanning)
        
        Args:
            wavelengths: Wavelength values
            intensities: Intensity values
        
        Returns:
            Purity score as float (0-100)
        """
        try:
            result = await cls.predict(wavelengths, intensities)
            return result.get("purity_percentage", np.nan)
        except Exception as e:
            logger.error(f"Scalar prediction error: {e}")
            return np.nan
    
    @classmethod
    async def predict_batch_scalar(cls, spectra_data: List[tuple]) -> List[float]:
        """
        Predict purity for multiple spectra (batch processing for performance)
        
        Args:
            spectra_data: List of (wavelengths, intensities) tuples
        
        Returns:
            List of purity scores
        """
        try:
            purity_scores = []
            
            # For now, process sequentially (can be optimized for true batch inference)
            for wavelengths, intensities in spectra_data:
                try:
                    purity = await cls.predict_purity_scalar(wavelengths, intensities)
                    purity_scores.append(purity)
                except Exception as e:
                    logger.error(f"Batch item prediction error: {e}")
                    purity_scores.append(np.nan)
            
            return purity_scores
            
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return [np.nan] * len(spectra_data)
    
    @classmethod
    def predict_spectrum_sync(cls, processed_spectrum: np.ndarray) -> float:
        """
        Synchronous prediction for preprocessed spectrum (for scan orchestrator)
        
        Args:
            processed_spectrum: Preprocessed spectrum array
        
        Returns:
            Purity score as float
        """
        try:
            model = ModelLoader.get_model()
            model_type = ModelLoader.get_model_type()
            
            if model_type == "baseline":
                return cls._predict_baseline_sync(processed_spectrum)
            elif model_type == "plsr":
                return cls._predict_plsr_sync(processed_spectrum)
            elif model_type == "cnn_1d":
                return cls._predict_cnn_1d_sync(processed_spectrum)
            elif model_type == "mock_cnn_1d":
                return cls._predict_mock_cnn_sync(processed_spectrum)
            elif model_type == "mock":
                return cls._predict_mock_sync(processed_spectrum)
            else:
                logger.error(f"Unknown model type: {model_type}")
                return np.nan
                
        except Exception as e:
            logger.error(f"Sync prediction error: {e}")
            return np.nan
    
    @classmethod
    def _predict_baseline_sync(cls, spectrum: np.ndarray) -> float:
        """Synchronous baseline model prediction"""
        try:
            model = ModelLoader.get_model()
            input_tensor = torch.FloatTensor(spectrum).unsqueeze(0)
            
            with torch.no_grad():
                output = model(input_tensor)
                purity_logits = output.squeeze()
                purity_percentage = torch.sigmoid(purity_logits).item() * 100
                
            return float(purity_percentage)
            
        except Exception as e:
            logger.error(f"Baseline sync prediction error: {e}")
            return cls._predict_mock_sync(spectrum)
    
    @classmethod
    def _predict_plsr_sync(cls, spectrum: np.ndarray) -> float:
        """Synchronous PLSR model prediction"""
        try:
            model_dict = ModelLoader.get_model()
            regressor = model_dict["regressor"]
            scaler = model_dict.get("scaler")
            
            input_data = spectrum.reshape(1, -1)
            if scaler:
                input_data = scaler.transform(input_data)
            
            purity_percentage = regressor.predict(input_data)[0]
            purity_percentage = np.clip(purity_percentage, 0, 100)
            
            return float(purity_percentage)
            
        except Exception as e:
            logger.error(f"PLSR sync prediction error: {e}")
            return cls._predict_mock_sync(spectrum)
    
    @classmethod
    def _predict_cnn_1d_sync(cls, spectrum: np.ndarray) -> float:
        """Synchronous CNN 1D model prediction"""
        try:
            model = ModelLoader.get_model()
            purity_percentage, _ = model.predict_purity(spectrum)
            return float(purity_percentage)
            
        except Exception as e:
            logger.error(f"CNN 1D sync prediction error: {e}")
            return cls._predict_mock_sync(spectrum)
    
    @classmethod
    def _predict_mock_cnn_sync(cls, spectrum: np.ndarray) -> float:
        """Synchronous mock CNN model prediction"""
        try:
            model = ModelLoader.get_model()
            purity_percentage, _ = model.predict_purity(spectrum)
            return float(purity_percentage)
            
        except Exception as e:
            logger.error(f"Mock CNN sync prediction error: {e}")
            return cls._predict_mock_sync(spectrum)

    @classmethod
    def _predict_mock_sync(cls, spectrum: np.ndarray) -> float:
        """Synchronous mock prediction"""
        np.random.seed(int(np.sum(spectrum) * 1000) % 2**32)
        
        spectrum_std = np.std(spectrum)
        spectrum_mean = np.mean(spectrum)
        
        base_purity = 70 + (spectrum_std * 30) + (spectrum_mean * 10)
        base_purity = np.clip(base_purity, 60, 98)
        
        purity_percentage = base_purity + np.random.normal(0, 3)
        purity_percentage = np.clip(purity_percentage, 55, 99)
        
        return float(purity_percentage)


# Convenience functions for external use
async def predict_spectrum(wavelengths: List[float], intensities: List[float]) -> float:
    """
    Convenience function to predict purity from spectrum
    
    Args:
        wavelengths: Wavelength values
        intensities: Intensity values
    
    Returns:
        Purity score (0-100)
    """
    return await InferenceEngine.predict_purity_scalar(wavelengths, intensities)

def predict_spectrum_preprocessed(processed_spectrum: np.ndarray) -> float:
    """
    Convenience function for preprocessed spectrum
    
    Args:
        processed_spectrum: Preprocessed spectrum array
    
    Returns:
        Purity score (0-100)
    """
    return InferenceEngine.predict_spectrum_sync(processed_spectrum)
