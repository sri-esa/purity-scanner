# 🧬 PurityScan ML Service API Documentation

## Base URL
```
http://localhost:8001/api/ml
```

## Authentication
Currently, the ML service does not require authentication. It's designed to be called internally by the Node.js backend.

## Endpoints

### Health Check

#### `GET /health`
Check the health status of the ML service.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "baseline",
  "uptime_seconds": 3600.5,
  "timestamp": "2025-10-17T13:19:00Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is degraded (model not loaded)

---

### Simple Status

#### `GET /status`
Get basic service status information.

**Response:**
```json
{
  "service": "PurityScan ML Service",
  "status": "running",
  "environment": "development"
}
```

---

### Analyze Spectrum

#### `POST /analyze`
Analyze a Raman spectrum for purity determination.

**Request Body:**
```json
{
  "wavelengths": [200.0, 201.0, 202.0, ...],
  "intensities": [0.1, 0.15, 0.12, ...]
}
```

**Request Validation:**
- Both arrays must have the same length
- Minimum 100 data points required
- Maximum 5000 data points allowed
- Wavelengths must be positive and in ascending order
- Intensities must be non-negative

**Response:**
```json
{
  "purity_percentage": 87.5,
  "confidence_score": 0.92,
  "contaminants": ["organic_compounds", "crystalline_impurities"],
  "model_used": "baseline",
  "processing_time_ms": 145.2,
  "timestamp": "2025-10-17T13:19:00Z"
}
```

**Response Fields:**
- `purity_percentage` (float): Purity percentage (0-100)
- `confidence_score` (float): Confidence in prediction (0-1)
- `contaminants` (array): List of detected contaminants (optional)
- `model_used` (string): ML model used for analysis
- `processing_time_ms` (float): Processing time in milliseconds
- `timestamp` (string): Analysis timestamp (ISO 8601)

**Status Codes:**
- `200 OK` - Analysis successful
- `400 Bad Request` - Invalid input data
- `422 Unprocessable Entity` - Validation error
- `503 Service Unavailable` - ML model not available

**Error Response:**
```json
{
  "error": "Invalid spectrum data",
  "detail": "Wavelengths and intensities must have the same length",
  "timestamp": "2025-10-17T13:19:00Z"
}
```

---

### Available Models

#### `GET /models`
Get information about available ML models.

**Response:**
```json
[
  {
    "name": "PurityScan Baseline",
    "type": "baseline",
    "version": "1.0.0",
    "accuracy": 0.92,
    "description": "HuggingFace transformer model for purity analysis"
  },
  {
    "name": "PLSR Purity Model",
    "type": "plsr",
    "version": "1.0.0",
    "accuracy": 0.89,
    "description": "Partial Least Squares Regression model"
  }
]
```

---

### Load Model

#### `POST /models/{model_name}/load`
Load a specific model by name.

**Path Parameters:**
- `model_name` (string): Name of the model to load

**Response:**
```json
{
  "message": "Model baseline loaded successfully"
}
```

**Status Codes:**
- `200 OK` - Model loaded successfully
- `400 Bad Request` - Failed to load model
- `500 Internal Server Error` - Internal error

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error information (optional)",
  "timestamp": "2025-10-17T13:19:00Z"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request data
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service not ready

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider:
- Request rate limiting per client
- Concurrent request limits
- Queue management for heavy processing

---

## Examples

### cURL Examples

**Health Check:**
```bash
curl -X GET http://localhost:8001/api/ml/health
```

**Analyze Spectrum:**
```bash
curl -X POST http://localhost:8001/api/ml/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "wavelengths": [200, 300, 400, 500, 600],
    "intensities": [0.1, 0.2, 0.15, 0.3, 0.25]
  }'
```

**Get Available Models:**
```bash
curl -X GET http://localhost:8001/api/ml/models
```

### Python Examples

```python
import requests
import numpy as np

# Health check
response = requests.get("http://localhost:8001/api/ml/health")
print(response.json())

# Analyze spectrum
wavelengths = np.linspace(200, 3500, 1024).tolist()
intensities = (0.5 + 0.3 * np.sin(np.array(wavelengths) / 500)).tolist()

response = requests.post(
    "http://localhost:8001/api/ml/analyze",
    json={
        "wavelengths": wavelengths,
        "intensities": intensities
    }
)

result = response.json()
print(f"Purity: {result['purity_percentage']:.2f}%")
print(f"Confidence: {result['confidence_score']:.3f}")
```

### JavaScript Examples

```javascript
// Health check
const healthResponse = await fetch('http://localhost:8001/api/ml/health');
const healthData = await healthResponse.json();
console.log(healthData);

// Analyze spectrum
const spectrumData = {
  wavelengths: Array.from({length: 1024}, (_, i) => 200 + i * 3.2),
  intensities: Array.from({length: 1024}, () => Math.random())
};

const analyzeResponse = await fetch('http://localhost:8001/api/ml/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(spectrumData)
});

const result = await analyzeResponse.json();
console.log(`Purity: ${result.purity_percentage}%`);
```

---

## Integration with Node.js Backend

The ML service is designed to be called by the Node.js backend:

```javascript
// backend/src/services/mlservice.js
const response = await axios.post(
  `${ML_SERVICE_URL}/api/ml/analyze`,
  { wavelengths, intensities },
  { timeout: 30000 }
);
```

---

## Performance Considerations

- **Typical Response Time**: 100-200ms per spectrum
- **Throughput**: ~10-20 requests/second (single worker)
- **Memory Usage**: ~500MB (baseline model)
- **CPU Usage**: High during inference, low during idle

### Optimization Tips

1. **Batch Processing**: Process multiple spectra in single request
2. **Model Caching**: Keep models loaded in memory
3. **GPU Acceleration**: Use CUDA for faster inference
4. **Load Balancing**: Deploy multiple instances behind load balancer

---

## Monitoring and Logging

### Health Monitoring
- Use `/health` endpoint for health checks
- Monitor response times and error rates
- Set up alerts for service degradation

### Logging
- API logs: `logs/api/ml_service.log`
- Training logs: `logs/training/`
- Log rotation and compression enabled

### Metrics to Monitor
- Request rate and response time
- Model inference time
- Memory and CPU usage
- Error rates by endpoint
- Model accuracy over time
