import pytest
import numpy as np
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestHealthAPI:
    """Test health check endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/ml/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "uptime_seconds" in data
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = client.get("/api/ml/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "PurityScan ML Service"
        assert data["status"] == "running"

class TestAnalyzeAPI:
    """Test analysis endpoints"""
    
    def test_analyze_valid_spectrum(self):
        """Test analysis with valid spectrum data"""
        # Generate test spectrum
        wavelengths = np.linspace(200, 3500, 512).tolist()
        intensities = (0.5 + 0.3 * np.sin(np.array(wavelengths) / 500) + 
                      0.1 * np.random.random(len(wavelengths))).tolist()
        
        response = client.post("/api/ml/analyze", json={
            "wavelengths": wavelengths,
            "intensities": intensities
        })
        
        assert response.status_code == 200
        
        data = response.json()
        assert "purity_percentage" in data
        assert "confidence_score" in data
        assert "model_used" in data
        assert "processing_time_ms" in data
        
        # Validate ranges
        assert 0 <= data["purity_percentage"] <= 100
        assert 0 <= data["confidence_score"] <= 1
        assert data["processing_time_ms"] > 0
    
    def test_analyze_invalid_spectrum_length_mismatch(self):
        """Test analysis with mismatched array lengths"""
        response = client.post("/api/ml/analyze", json={
            "wavelengths": [200, 300, 400],
            "intensities": [0.1, 0.2]  # Different length
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_spectrum_too_short(self):
        """Test analysis with spectrum too short"""
        response = client.post("/api/ml/analyze", json={
            "wavelengths": [200, 300],
            "intensities": [0.1, 0.2]
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_empty_spectrum(self):
        """Test analysis with empty spectrum"""
        response = client.post("/api/ml/analyze", json={
            "wavelengths": [],
            "intensities": []
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_invalid_data_types(self):
        """Test analysis with invalid data types"""
        response = client.post("/api/ml/analyze", json={
            "wavelengths": "not_a_list",
            "intensities": [0.1, 0.2, 0.3]
        })
        
        assert response.status_code == 422  # Validation error

class TestModelsAPI:
    """Test model management endpoints"""
    
    def test_get_available_models(self):
        """Test getting available models"""
        response = client.get("/api/ml/models")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Should have at least the mock model
        assert len(data) >= 1
        
        # Check model structure
        for model in data:
            assert "name" in model
            assert "type" in model
            assert "version" in model
            assert "description" in model

class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "PurityScan ML Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"

@pytest.fixture
def sample_spectrum():
    """Generate a sample spectrum for testing"""
    wavelengths = np.linspace(200, 3500, 1024)
    intensities = (0.5 + 0.3 * np.sin(wavelengths / 500) + 
                  0.1 * np.random.random(len(wavelengths)))
    return wavelengths.tolist(), intensities.tolist()

class TestSpectrumValidation:
    """Test spectrum validation"""
    
    def test_valid_spectrum(self, sample_spectrum):
        """Test with valid spectrum"""
        wavelengths, intensities = sample_spectrum
        
        response = client.post("/api/ml/analyze", json={
            "wavelengths": wavelengths,
            "intensities": intensities
        })
        
        assert response.status_code == 200
    
    def test_negative_wavelengths(self):
        """Test with negative wavelengths"""
        response = client.post("/api/ml/analyze", json={
            "wavelengths": [-100, 200, 300],
            "intensities": [0.1, 0.2, 0.3]
        })
        
        assert response.status_code == 422
    
    def test_negative_intensities(self):
        """Test with negative intensities"""
        response = client.post("/api/ml/analyze", json={
            "wavelengths": [200, 300, 400],
            "intensities": [-0.1, 0.2, 0.3]
        })
        
        assert response.status_code == 422
