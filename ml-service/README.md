# 🧬 PurityScan ML Service

Machine Learning microservice for Raman spectroscopy purity analysis.

## 🚀 Quick Start

### Local Development

1. **Create virtual environment**
```bash
cd ml-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Generate test data**
```bash
python scripts/generate_fake_data.py --samples 1000 --output data
```

5. **Run the service**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker Deployment

```bash
# Build and run ML service only
docker-compose build ml-service
docker-compose up ml-service

# Or run entire stack
docker-compose up
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/ml/health
```

### Analyze Spectrum
```bash
POST /api/ml/analyze
Content-Type: application/json

{
  "wavelengths": [200, 201, 202, ...],
  "intensities": [0.1, 0.15, 0.12, ...]
}
```

Response:
```json
{
  "purity_percentage": 87.5,
  "confidence_score": 0.92,
  "contaminants": ["organic_compounds"],
  "model_used": "baseline",
  "processing_time_ms": 145.2,
  "timestamp": "2025-10-17T13:19:00Z"
}
```

### Available Models
```bash
GET /api/ml/models
```

## 🏗️ Architecture

```
ml-service/
├── main.py                 # FastAPI application
├── config.py              # Configuration
├── src/
│   ├── api/               # API routes
│   ├── core/              # ML logic
│   ├── models/            # Model architectures
│   └── utils/             # Utilities
├── models/                # Saved models
├── data/                  # Training data
├── scripts/               # Utility scripts
└── tests/                 # Unit tests
```

## 🔧 Configuration

Environment variables (`.env`):

- `MODEL_TYPE`: Model to use (`baseline`, `plsr`, `mock`)
- `DEVICE`: Compute device (`cpu`, `cuda`)
- `API_PORT`: Service port (default: 8001)
- `LOG_LEVEL`: Logging level (`INFO`, `DEBUG`)

## 🧪 Models

### Baseline Model
- HuggingFace transformer adapted for spectral data
- High accuracy for complex spectra
- Requires more computational resources

### PLSR Model
- Partial Least Squares Regression
- Fast inference
- Good for linear relationships

### Mock Model
- For testing and development
- Generates realistic fake results
- No ML dependencies required

## 🔄 Integration

The ML service integrates with the Node.js backend via HTTP:

```javascript
// backend/src/services/mlservice.js
const response = await axios.post('http://ml-service:8001/api/ml/analyze', {
  wavelengths: [...],
  intensities: [...]
});
```

## 📊 Data Flow

```
Frontend (React) 
    ↓ HTTP Request
Backend (Node.js) 
    ↓ HTTP Request
ML Service (Python/FastAPI) 
    ↓ Preprocessing
    ↓ Model Inference
    ↓ Post-processing
    ↓ JSON Response
Backend (Node.js) 
    ↓ Database Storage
    ↓ Response
Frontend (React)
```

## 🧬 Preprocessing Pipeline

1. **Baseline Removal** - Remove spectral baseline
2. **Smoothing** - Reduce noise with Savitzky-Golay filter
3. **Resampling** - Normalize to fixed length (1024 points)
4. **Normalization** - Scale intensities (MinMax/Standard)

## 🎯 Performance

- **Inference Time**: ~100-200ms per spectrum
- **Memory Usage**: ~500MB (baseline model)
- **Throughput**: ~10-20 requests/second
- **Accuracy**: 85-95% (depending on model and data quality)

## 🔍 Testing

```bash
# Run unit tests
pytest tests/

# Test API endpoints
python -m pytest tests/test_api.py -v

# Load testing
# Use tools like wrk or artillery for load testing
```

## 📈 Monitoring

Health check endpoint provides:
- Service status
- Model loading status
- Uptime
- Memory usage

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure proper logging
- [ ] Set up model persistence
- [ ] Configure resource limits
- [ ] Set up monitoring/alerting
- [ ] Enable HTTPS
- [ ] Configure CORS properly

### Scaling

- Use multiple workers: `--workers 4`
- Load balancer for multiple instances
- GPU acceleration for heavy models
- Model caching and optimization

## 🔧 Troubleshooting

### Common Issues

1. **Model not loading**
   - Check model file paths
   - Verify file permissions
   - Check available memory

2. **Slow inference**
   - Use GPU if available
   - Optimize model size
   - Batch processing

3. **Memory issues**
   - Reduce model size
   - Implement model quantization
   - Use streaming for large datasets

### Logs

Check logs in `logs/api/` and `logs/training/` directories.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.
