# src/hardware/spectrometer.py
import numpy as np
import time
import logging
from typing import Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SpectrometerConfig:
    """Configuration for spectrometer"""
    wavelength_min: float = 400.0  # nm
    wavelength_max: float = 1800.0  # nm
    num_pixels: int = 1024
    integration_time_min: float = 0.001  # seconds
    integration_time_max: float = 10.0  # seconds
    default_integration_time: float = 0.1  # seconds

class SpectrometerController:
    """
    Mock spectrometer controller for Raman spectroscopy
    
    In production, replace with actual spectrometer SDK:
    - Ocean Optics (SeaBreeze)
    - Andor (SDK)
    - Princeton Instruments
    - Horiba/Jobin Yvon
    - Custom USB/Ethernet spectrometers
    """
    
    def __init__(self, config: Optional[SpectrometerConfig] = None):
        self.config = config or SpectrometerConfig()
        self.is_connected = False
        self.wavelengths = np.linspace(
            self.config.wavelength_min, 
            self.config.wavelength_max, 
            self.config.num_pixels
        )
        
        # Simulate some baseline noise characteristics
        self.dark_spectrum = np.random.normal(0, 10, self.config.num_pixels)
        self.reference_spectrum = self._generate_reference_spectrum()
        
    def connect(self, device_id: Optional[str] = None):
        """
        Connect to spectrometer hardware
        
        Args:
            device_id: Device identifier (serial number, USB address, etc.)
        """
        try:
            # TODO: Replace with actual hardware connection
            # Examples:
            # - Ocean Optics: self.spec = seabreeze.spectrometers.Spectrometer.from_serial_number(device_id)
            # - Andor: self.spec = andor.CCD()
            # - Custom: self.spec = CustomSpectrometer(device_id)
            
            logger.info(f"Connecting to spectrometer {device_id or 'default'}")
            time.sleep(0.5)  # Simulate connection time
            self.is_connected = True
            logger.info("✅ Spectrometer connected")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to spectrometer: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from spectrometer"""
        try:
            self.is_connected = False
            logger.info("Spectrometer disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting spectrometer: {e}")
    
    def read_spectrum(self, integration_time: float = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read a single spectrum
        
        Args:
            integration_time: Integration time in seconds
            
        Returns:
            Tuple of (wavelengths, intensities)
        """
        if not self.is_connected:
            raise RuntimeError("Spectrometer not connected")
            
        if integration_time is None:
            integration_time = self.config.default_integration_time
            
        if not (self.config.integration_time_min <= integration_time <= self.config.integration_time_max):
            raise ValueError(f"Integration time must be between {self.config.integration_time_min} and {self.config.integration_time_max} seconds")
        
        # Simulate acquisition time
        time.sleep(integration_time)
        
        # TODO: Replace with actual hardware read
        # Examples:
        # - Ocean Optics: intensities = self.spec.intensities()
        # - Andor: intensities = self.spec.GetAcquiredData()
        # - Custom: intensities = self.spec.read_spectrum()
        
        # Generate realistic mock spectrum
        intensities = self._generate_mock_spectrum(integration_time)
        
        return self.wavelengths.copy(), intensities
    
    def read_dark_spectrum(self, integration_time: float = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read dark spectrum (with laser off or shutter closed)
        
        Args:
            integration_time: Integration time in seconds
            
        Returns:
            Tuple of (wavelengths, dark_intensities)
        """
        if integration_time is None:
            integration_time = self.config.default_integration_time
            
        time.sleep(integration_time)
        
        # Dark spectrum is mostly noise
        dark_intensities = self.dark_spectrum + np.random.normal(0, 5, self.config.num_pixels)
        
        return self.wavelengths.copy(), dark_intensities
    
    def read_reference_spectrum(self, integration_time: float = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read reference spectrum (from known reference material)
        
        Args:
            integration_time: Integration time in seconds
            
        Returns:
            Tuple of (wavelengths, reference_intensities)
        """
        if integration_time is None:
            integration_time = self.config.default_integration_time
            
        time.sleep(integration_time)
        
        # Scale reference by integration time
        ref_intensities = self.reference_spectrum * integration_time / self.config.default_integration_time
        ref_intensities += np.random.normal(0, 10, self.config.num_pixels)  # Add noise
        
        return self.wavelengths.copy(), ref_intensities
    
    def set_integration_time(self, integration_time: float):
        """
        Set default integration time
        
        Args:
            integration_time: Integration time in seconds
        """
        if not (self.config.integration_time_min <= integration_time <= self.config.integration_time_max):
            raise ValueError(f"Integration time must be between {self.config.integration_time_min} and {self.config.integration_time_max} seconds")
        
        self.config.default_integration_time = integration_time
        logger.info(f"Integration time set to {integration_time:.3f} seconds")
    
    def get_wavelengths(self) -> np.ndarray:
        """Get wavelength array"""
        return self.wavelengths.copy()
    
    def get_status(self) -> dict:
        """Get spectrometer status"""
        return {
            "connected": self.is_connected,
            "integration_time": self.config.default_integration_time,
            "wavelength_range": (self.config.wavelength_min, self.config.wavelength_max),
            "num_pixels": self.config.num_pixels
        }
    
    def _generate_reference_spectrum(self) -> np.ndarray:
        """Generate a realistic reference spectrum (e.g., silicon or polystyrene)"""
        # Create some characteristic peaks for a reference material
        spectrum = np.zeros(self.config.num_pixels)
        
        # Add some Raman peaks at typical wavenumbers
        peak_positions = [520, 800, 1000, 1200, 1600]  # Example wavenumber positions
        
        for peak_wn in peak_positions:
            # Convert wavenumber to wavelength index (simplified)
            peak_idx = int((peak_wn - 400) / (1800 - 400) * self.config.num_pixels)
            if 0 <= peak_idx < self.config.num_pixels:
                # Add Gaussian peak
                sigma = 10  # Peak width
                for i in range(max(0, peak_idx - 3*sigma), min(self.config.num_pixels, peak_idx + 3*sigma)):
                    spectrum[i] += 1000 * np.exp(-0.5 * ((i - peak_idx) / sigma)**2)
        
        # Add baseline
        spectrum += 100 + 50 * np.sin(np.linspace(0, 4*np.pi, self.config.num_pixels))
        
        return spectrum
    
    def _generate_mock_spectrum(self, integration_time: float) -> np.ndarray:
        """Generate a realistic mock Raman spectrum"""
        # Start with noise
        spectrum = np.random.normal(0, 20, self.config.num_pixels)
        
        # Add some random Raman peaks (simulating different materials)
        num_peaks = np.random.randint(3, 8)
        for _ in range(num_peaks):
            peak_idx = np.random.randint(50, self.config.num_pixels - 50)
            peak_intensity = np.random.uniform(100, 1000) * integration_time / self.config.default_integration_time
            peak_width = np.random.uniform(5, 20)
            
            # Add Gaussian peak
            for i in range(max(0, int(peak_idx - 3*peak_width)), 
                          min(self.config.num_pixels, int(peak_idx + 3*peak_width))):
                spectrum[i] += peak_intensity * np.exp(-0.5 * ((i - peak_idx) / peak_width)**2)
        
        # Add baseline (fluorescence background)
        baseline_level = np.random.uniform(50, 200)
        baseline_slope = np.random.uniform(-0.1, 0.1)
        x = np.linspace(0, 1, self.config.num_pixels)
        spectrum += baseline_level + baseline_slope * x * 100
        
        # Scale by integration time
        spectrum *= integration_time / self.config.default_integration_time
        
        # Ensure non-negative
        spectrum = np.maximum(spectrum, 0)
        
        return spectrum
    
    def __enter__(self):
        """Context manager entry"""
        if not self.is_connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
