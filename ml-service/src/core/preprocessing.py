import numpy as np
from scipy import signal
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)

class SpectrumPreprocessor:
    """
    Preprocessing utilities for Raman spectroscopy data
    """
    
    def __init__(self):
        self.scaler = None
        self.target_length = 1024
    
    def normalize_spectrum(self, intensities: np.ndarray, method: str = "minmax") -> np.ndarray:
        """
        Normalize spectrum intensities
        
        Args:
            intensities: Raw intensity values
            method: Normalization method ('minmax', 'standard', 'l2')
        
        Returns:
            Normalized intensities
        """
        intensities = np.array(intensities)
        
        if method == "minmax":
            return (intensities - intensities.min()) / (intensities.max() - intensities.min() + 1e-8)
        elif method == "standard":
            return (intensities - intensities.mean()) / (intensities.std() + 1e-8)
        elif method == "l2":
            return intensities / (np.linalg.norm(intensities) + 1e-8)
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    def remove_baseline(self, intensities: np.ndarray, method: str = "polynomial") -> np.ndarray:
        """
        Remove baseline from spectrum
        
        Args:
            intensities: Raw intensity values
            method: Baseline removal method
        
        Returns:
            Baseline-corrected intensities
        """
        intensities = np.array(intensities)
        
        if method == "polynomial":
            # Fit polynomial baseline and subtract
            x = np.arange(len(intensities))
            coeffs = np.polyfit(x, intensities, deg=3)
            baseline = np.polyval(coeffs, x)
            return intensities - baseline
        
        elif method == "rolling_minimum":
            # Rolling minimum baseline
            window_size = len(intensities) // 20
            baseline = signal.minimum_filter1d(intensities, size=window_size)
            return intensities - baseline
        
        else:
            return intensities
    
    def smooth_spectrum(self, intensities: np.ndarray, method: str = "savgol") -> np.ndarray:
        """
        Smooth spectrum to reduce noise
        
        Args:
            intensities: Intensity values
            method: Smoothing method
        
        Returns:
            Smoothed intensities
        """
        intensities = np.array(intensities)
        
        if method == "savgol":
            window_length = min(21, len(intensities) // 10)
            if window_length % 2 == 0:
                window_length += 1
            return signal.savgol_filter(intensities, window_length, polyorder=3)
        
        elif method == "gaussian":
            sigma = len(intensities) / 100
            return signal.gaussian_filter1d(intensities, sigma=sigma)
        
        else:
            return intensities
    
    def resample_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                         target_length: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Resample spectrum to fixed length
        
        Args:
            wavelengths: Wavelength values
            intensities: Intensity values
            target_length: Target number of points
        
        Returns:
            Resampled wavelengths and intensities
        """
        if target_length is None:
            target_length = self.target_length
        
        wavelengths = np.array(wavelengths)
        intensities = np.array(intensities)
        
        # Create uniform wavelength grid
        new_wavelengths = np.linspace(wavelengths.min(), wavelengths.max(), target_length)
        
        # Interpolate intensities
        new_intensities = np.interp(new_wavelengths, wavelengths, intensities)
        
        return new_wavelengths, new_intensities
    
    def preprocess_full(self, wavelengths: List[float], intensities: List[float]) -> np.ndarray:
        """
        Complete preprocessing pipeline
        
        Args:
            wavelengths: Raw wavelength values
            intensities: Raw intensity values
        
        Returns:
            Preprocessed spectrum ready for ML model
        """
        try:
            # Convert to numpy arrays
            wavelengths = np.array(wavelengths)
            intensities = np.array(intensities)
            
            # Validate input
            if len(wavelengths) != len(intensities):
                raise ValueError("Wavelengths and intensities must have same length")
            
            if len(intensities) < 50:
                raise ValueError("Spectrum too short for reliable analysis")
            
            # Remove any NaN or infinite values
            mask = np.isfinite(wavelengths) & np.isfinite(intensities)
            wavelengths = wavelengths[mask]
            intensities = intensities[mask]
            
            # Preprocessing steps
            logger.debug("Starting spectrum preprocessing...")
            
            # 1. Remove baseline
            intensities = self.remove_baseline(intensities, method="polynomial")
            
            # 2. Smooth spectrum
            intensities = self.smooth_spectrum(intensities, method="savgol")
            
            # 3. Resample to fixed length
            wavelengths, intensities = self.resample_spectrum(wavelengths, intensities)
            
            # 4. Normalize
            intensities = self.normalize_spectrum(intensities, method="minmax")
            
            logger.debug(f"Preprocessing complete. Output shape: {intensities.shape}")
            
            return intensities
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            raise ValueError(f"Failed to preprocess spectrum: {e}")
    
    def detect_outliers(self, intensities: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        Detect outlier points in spectrum
        
        Args:
            intensities: Intensity values
            threshold: Z-score threshold for outliers
        
        Returns:
            Boolean mask of outliers
        """
        z_scores = np.abs((intensities - np.mean(intensities)) / np.std(intensities))
        return z_scores > threshold
    
    def validate_spectrum(self, wavelengths: List[float], intensities: List[float]) -> bool:
        """
        Validate spectrum data quality
        
        Args:
            wavelengths: Wavelength values
            intensities: Intensity values
        
        Returns:
            True if spectrum is valid for analysis
        """
        try:
            wavelengths = np.array(wavelengths)
            intensities = np.array(intensities)
            
            # Check lengths
            if len(wavelengths) != len(intensities):
                return False
            
            if len(intensities) < 100:
                return False
            
            # Check for valid ranges
            if np.any(wavelengths <= 0) or np.any(intensities < 0):
                return False
            
            # Check for too many zeros or constant values
            if np.sum(intensities == 0) > len(intensities) * 0.5:
                return False
            
            if np.std(intensities) < 1e-6:
                return False
            
            return True
            
        except Exception:
            return False
