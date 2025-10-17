import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SpectrumValidator:
    """
    Validation utilities for spectrum data
    """
    
    @staticmethod
    def validate_spectrum_data(wavelengths: List[float], intensities: List[float]) -> Tuple[bool, Optional[str]]:
        """
        Validate spectrum data for analysis
        
        Args:
            wavelengths: List of wavelength values
            intensities: List of intensity values
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Convert to numpy arrays for validation
            wavelengths = np.array(wavelengths)
            intensities = np.array(intensities)
            
            # Check if arrays are not empty
            if len(wavelengths) == 0 or len(intensities) == 0:
                return False, "Spectrum data cannot be empty"
            
            # Check if arrays have same length
            if len(wavelengths) != len(intensities):
                return False, f"Wavelengths ({len(wavelengths)}) and intensities ({len(intensities)}) must have same length"
            
            # Check minimum length
            if len(wavelengths) < 100:
                return False, f"Spectrum too short ({len(wavelengths)} points). Minimum 100 points required"
            
            # Check maximum length
            if len(wavelengths) > 5000:
                return False, f"Spectrum too long ({len(wavelengths)} points). Maximum 5000 points allowed"
            
            # Check for valid numeric values
            if not np.all(np.isfinite(wavelengths)):
                return False, "Wavelengths contain invalid values (NaN or infinity)"
            
            if not np.all(np.isfinite(intensities)):
                return False, "Intensities contain invalid values (NaN or infinity)"
            
            # Check wavelength range
            if np.any(wavelengths <= 0):
                return False, "Wavelengths must be positive"
            
            if np.min(wavelengths) > 10000 or np.max(wavelengths) < 100:
                return False, f"Wavelength range ({np.min(wavelengths):.1f} - {np.max(wavelengths):.1f}) outside typical Raman range"
            
            # Check intensity range
            if np.any(intensities < 0):
                return False, "Intensities cannot be negative"
            
            # Check for constant values
            if np.std(intensities) < 1e-10:
                return False, "Intensities appear to be constant (no variation detected)"
            
            # Check for too many zeros
            zero_fraction = np.sum(intensities == 0) / len(intensities)
            if zero_fraction > 0.8:
                return False, f"Too many zero values ({zero_fraction*100:.1f}% of spectrum)"
            
            # Check wavelength ordering
            if not np.all(np.diff(wavelengths) > 0):
                return False, "Wavelengths must be in ascending order"
            
            # Check for reasonable intensity range
            intensity_range = np.max(intensities) - np.min(intensities)
            if intensity_range < 1e-6:
                return False, "Intensity range too small for reliable analysis"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, f"Validation failed: {str(e)}"
    
    @staticmethod
    def validate_wavelength_range(wavelengths: np.ndarray, min_wl: float = 100, max_wl: float = 4000) -> bool:
        """
        Check if wavelength range is suitable for Raman analysis
        
        Args:
            wavelengths: Wavelength array
            min_wl: Minimum acceptable wavelength
            max_wl: Maximum acceptable wavelength
        
        Returns:
            True if range is acceptable
        """
        return (np.min(wavelengths) >= min_wl and 
                np.max(wavelengths) <= max_wl and
                (np.max(wavelengths) - np.min(wavelengths)) > 500)
    
    @staticmethod
    def detect_anomalies(intensities: np.ndarray, threshold: float = 5.0) -> List[int]:
        """
        Detect anomalous points in spectrum
        
        Args:
            intensities: Intensity array
            threshold: Z-score threshold for anomaly detection
        
        Returns:
            List of indices of anomalous points
        """
        z_scores = np.abs((intensities - np.mean(intensities)) / np.std(intensities))
        anomalies = np.where(z_scores > threshold)[0]
        return anomalies.tolist()
    
    @staticmethod
    def estimate_snr(intensities: np.ndarray) -> float:
        """
        Estimate signal-to-noise ratio
        
        Args:
            intensities: Intensity array
        
        Returns:
            Estimated SNR
        """
        # Simple SNR estimation using signal std vs noise std
        signal_power = np.var(intensities)
        
        # Estimate noise from high-frequency components
        diff = np.diff(intensities)
        noise_power = np.var(diff) / 2  # Factor of 2 for differencing
        
        if noise_power == 0:
            return float('inf')
        
        snr = 10 * np.log10(signal_power / noise_power)
        return max(0, snr)  # Return 0 for very noisy signals

class ModelValidator:
    """
    Validation utilities for ML models
    """
    
    @staticmethod
    def validate_prediction_output(prediction: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate ML model prediction output
        
        Args:
            prediction: Model prediction dictionary
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_keys = ['purity_percentage', 'confidence_score']
        
        # Check required keys
        for key in required_keys:
            if key not in prediction:
                return False, f"Missing required key: {key}"
        
        # Validate purity percentage
        purity = prediction['purity_percentage']
        if not isinstance(purity, (int, float)):
            return False, "Purity percentage must be numeric"
        
        if not (0 <= purity <= 100):
            return False, f"Purity percentage ({purity}) must be between 0 and 100"
        
        # Validate confidence score
        confidence = prediction['confidence_score']
        if not isinstance(confidence, (int, float)):
            return False, "Confidence score must be numeric"
        
        if not (0 <= confidence <= 1):
            return False, f"Confidence score ({confidence}) must be between 0 and 1"
        
        # Validate contaminants if present
        if 'contaminants' in prediction:
            contaminants = prediction['contaminants']
            if contaminants is not None and not isinstance(contaminants, list):
                return False, "Contaminants must be a list or None"
        
        return True, None
