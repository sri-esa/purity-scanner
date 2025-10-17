from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional
from datetime import datetime

class SpectrumData(BaseModel):
    """Input model for spectrum analysis"""
    wavelengths: List[float] = Field(..., description="Array of wavelength values")
    intensities: List[float] = Field(..., description="Array of intensity values")
    
    @validator('wavelengths', 'intensities')
    def validate_arrays(cls, v):
        if len(v) < 100:
            raise ValueError('Spectrum must have at least 100 data points')
        if len(v) > 5000:
            raise ValueError('Spectrum cannot exceed 5000 data points')
        return v
    
    @validator('intensities')
    def validate_intensities_length(cls, v, values):
        if 'wavelengths' in values and len(v) != len(values['wavelengths']):
            raise ValueError('Wavelengths and intensities must have the same length')
        return v

class PurityResult(BaseModel):
    """Output model for purity analysis results"""
    model_config = ConfigDict(protected_namespaces=())
    
    purity_percentage: float = Field(..., description="Purity percentage (0-100)")
    confidence_score: float = Field(..., description="Confidence in the prediction (0-1)")
    contaminants: Optional[List[str]] = Field(default=None, description="Detected contaminants")
    model_used: str = Field(..., description="ML model used for analysis")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    """Health check response model"""
    model_config = ConfigDict(protected_namespaces=())
    
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    model_type: str = Field(..., description="Type of loaded model")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ModelInfo(BaseModel):
    """Model information"""
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type")
    version: str = Field(..., description="Model version")
    accuracy: Optional[float] = Field(default=None, description="Model accuracy")
    description: str = Field(..., description="Model description")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
