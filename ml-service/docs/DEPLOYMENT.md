# 🚀 PurityScan ML Service Deployment Guide

## Overview

This guide covers deploying the PurityScan ML Service in various environments, from local development to production.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- At least 2GB RAM (4GB+ recommended for production)
- CPU with AVX support (for optimal PyTorch performance)

---

## Local Development

### 1. Setup Environment

```bash
cd ml-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Generate Test Data

```bash
# Generate synthetic training data
python scripts/generate_fake_data.py --samples 1000 --output data

# This creates:
# - data/train_spectra.npy
# - data/train_labels.npy  
# - data/wavelengths.npy
# - data/metadata.json
```

### 3. Run Service

```bash
# Development mode with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Or production mode
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 2
```

### 4. Test Service

```bash
# Health check
curl http://localhost:8001/api/ml/health

# Test analysis
curl -X POST http://localhost:8001/api/ml/analyze \
  -H "Content-Type: application/json" \
  -d '{"wavelengths": [200,300,400], "intensities": [0.1,0.2,0.15]}'
```

---

## Docker Deployment

### 1. Build Image

```bash
# Build ML service image
docker build -t purity-ml-service .

# Or using docker-compose
docker-compose build ml-service
```

### 2. Run Container

```bash
# Run standalone container
docker run -d \
  --name purity-ml \
  -p 8001:8001 \
  -e MODEL_TYPE=baseline \
  -e DEVICE=cpu \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  purity-ml-service

# Or using docker-compose
docker-compose up ml-service
```

### 3. Full Stack Deployment

```bash
# Deploy entire application stack
docker-compose up -d

# Services started:
# - ml-service (port 8001)
# - backend (port 3000) 
# - frontend (port 80)
```

---

## Production Deployment

### 1. Environment Configuration

Create production `.env` file:

```bash
# Production environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Model settings
MODEL_TYPE=baseline
DEVICE=cpu  # or cuda if GPU available

# API settings
API_HOST=0.0.0.0
API_PORT=8001
WORKERS=4  # Adjust based on CPU cores

# Security
# Add any API keys or secrets here
```

### 2. Resource Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 2GB
- Storage: 5GB
- Network: 100 Mbps

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 20GB SSD
- Network: 1 Gbps
- GPU: Optional (NVIDIA with CUDA support)

### 3. Docker Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  ml-service:
    build: ./ml-service
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=production
      - MODEL_TYPE=baseline
      - WORKERS=4
    volumes:
      - ./ml-service/models:/app/models:ro
      - ./ml-service/logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/ml/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

### 4. Load Balancer Configuration

**Nginx Configuration:**
```nginx
upstream ml_service {
    server ml-service-1:8001;
    server ml-service-2:8001;
    server ml-service-3:8001;
}

server {
    listen 80;
    server_name ml-api.yourdomain.com;

    location /api/ml/ {
        proxy_pass http://ml_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

## Cloud Deployment

### AWS ECS

1. **Create Task Definition:**
```json
{
  "family": "purity-ml-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "ml-service",
      "image": "your-registry/purity-ml-service:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "MODEL_TYPE", "value": "baseline"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/purity-ml-service",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

2. **Create Service:**
```bash
aws ecs create-service \
  --cluster purity-cluster \
  --service-name ml-service \
  --task-definition purity-ml-service \
  --desired-count 2 \
  --launch-type FARGATE
```

### Google Cloud Run

```bash
# Build and push image
docker build -t gcr.io/your-project/purity-ml-service .
docker push gcr.io/your-project/purity-ml-service

# Deploy to Cloud Run
gcloud run deploy ml-service \
  --image gcr.io/your-project/purity-ml-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

### Azure Container Instances

```bash
az container create \
  --resource-group purity-rg \
  --name ml-service \
  --image your-registry/purity-ml-service:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8001 \
  --environment-variables \
    ENVIRONMENT=production \
    MODEL_TYPE=baseline
```

---

## Kubernetes Deployment

### 1. Deployment Manifest

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-service
  labels:
    app: ml-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-service
  template:
    metadata:
      labels:
        app: ml-service
    spec:
      containers:
      - name: ml-service
        image: purity-ml-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: MODEL_TYPE
          value: "baseline"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /api/ml/health
            port: 8001
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/ml/health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
```

### 2. Service Manifest

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-service
spec:
  selector:
    app: ml-service
  ports:
  - protocol: TCP
    port: 8001
    targetPort: 8001
  type: ClusterIP
```

### 3. Deploy

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## Monitoring and Observability

### 1. Health Checks

```bash
# Kubernetes health check
livenessProbe:
  httpGet:
    path: /api/ml/health
    port: 8001
  initialDelaySeconds: 60
  periodSeconds: 30

# Docker health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/api/ml/health')"
```

### 2. Logging

**Structured Logging:**
```python
# Configure loguru for structured logs
logger.add(
    sys.stdout,
    format="{time} | {level} | {message}",
    serialize=True  # JSON format
)
```

**Log Aggregation:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd + Elasticsearch
- AWS CloudWatch Logs
- Google Cloud Logging

### 3. Metrics

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('ml_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('ml_request_duration_seconds', 'Request latency')
MODEL_INFERENCE_TIME = Histogram('ml_inference_duration_seconds', 'Model inference time')
```

### 4. Alerting

**Example Alerts:**
- Service down (health check fails)
- High error rate (>5% 5xx responses)
- High latency (>1s p95 response time)
- High memory usage (>80%)
- Model inference failures

---

## Security Considerations

### 1. Network Security

```yaml
# Kubernetes NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ml-service-policy
spec:
  podSelector:
    matchLabels:
      app: ml-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend  # Only allow backend to access
    ports:
    - protocol: TCP
      port: 8001
```

### 2. Container Security

```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' mluser
USER mluser

# Read-only filesystem
docker run --read-only --tmpfs /tmp purity-ml-service
```

### 3. Secrets Management

```bash
# Kubernetes secrets
kubectl create secret generic ml-secrets \
  --from-literal=api-key=your-api-key

# Mount in deployment
volumeMounts:
- name: secrets
  mountPath: /etc/secrets
  readOnly: true
```

---

## Scaling Strategies

### 1. Horizontal Scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Vertical Scaling

```yaml
# Kubernetes VPA
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: ml-service-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-service
  updatePolicy:
    updateMode: "Auto"
```

### 3. Load Testing

```bash
# Using wrk
wrk -t12 -c400 -d30s --script=test_analyze.lua http://localhost:8001/api/ml/analyze

# Using artillery
artillery run load-test.yml
```

---

## Troubleshooting

### Common Issues

1. **Model Loading Fails**
   - Check model file paths and permissions
   - Verify available memory
   - Check logs for specific error messages

2. **High Memory Usage**
   - Monitor model size and batch processing
   - Implement model quantization
   - Use memory profiling tools

3. **Slow Response Times**
   - Profile inference pipeline
   - Consider GPU acceleration
   - Optimize preprocessing steps

4. **Container Startup Issues**
   - Increase health check initial delay
   - Check resource limits
   - Verify environment variables

### Debugging Commands

```bash
# Check container logs
docker logs purity-ml

# Execute into container
docker exec -it purity-ml bash

# Check resource usage
docker stats purity-ml

# Kubernetes debugging
kubectl logs deployment/ml-service
kubectl describe pod ml-service-xxx
kubectl exec -it ml-service-xxx -- bash
```

---

## Backup and Recovery

### 1. Model Backup

```bash
# Backup trained models
tar -czf models-backup-$(date +%Y%m%d).tar.gz models/

# Upload to cloud storage
aws s3 cp models-backup-*.tar.gz s3://your-backup-bucket/
```

### 2. Configuration Backup

```bash
# Backup configuration
kubectl get configmap ml-config -o yaml > ml-config-backup.yaml
kubectl get secret ml-secrets -o yaml > ml-secrets-backup.yaml
```

### 3. Disaster Recovery

```bash
# Restore from backup
aws s3 cp s3://your-backup-bucket/models-backup-latest.tar.gz .
tar -xzf models-backup-latest.tar.gz

# Redeploy service
kubectl apply -f k8s/
```

This deployment guide provides comprehensive coverage for deploying the PurityScan ML Service across different environments and platforms.
