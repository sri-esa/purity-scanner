# 2D Raman Spectroscopy Scanning System

## Overview

The Purity Vision Lab ML Service now includes comprehensive 2D scanning capabilities for automated Raman spectroscopy analysis. This system enables virtual 2D scanning by coordinating motorized stage movement, spectrum acquisition, ML inference, and visualization.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Demo Frontend │    │   FastAPI Server │    │  Hardware Layer │
│   (HTML/JS)     │◄──►│   (Python)       │◄──►│  (Mock/Real)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  ML Inference    │
                       │  (PyTorch/PLSR)  │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Visualization   │
                       │  (Matplotlib)    │
                       └──────────────────┘
```

## Key Components

### 1. Hardware Abstraction Layer

**Files:**
- `src/hardware/stage_controller.py` - X-Y motorized stage control
- `src/hardware/spectrometer.py` - Raman spectrometer interface

**Features:**
- Safe movement with bounds checking
- Emergency stop functionality
- Homing and position tracking
- Mock implementations for development/testing

### 2. Scan Orchestrator

**File:** `src/core/scan_orchestrator.py`

**Features:**
- Coordinates stage movement and spectrum acquisition
- Serpentine scanning patterns for efficiency
- Real-time progress tracking
- Pause/resume/cancel functionality
- Batch processing for performance
- Comprehensive error handling

### 3. ML Integration

**Enhanced Files:**
- `src/core/inference.py` - Added scalar prediction functions
- `src/core/model_loader.py` - Added model warmup and optimization

**Features:**
- Scalar purity prediction for 2D mapping
- Batch inference capabilities
- Model warmup to reduce first-inference latency
- TorchScript optimization for PyTorch models

### 4. Visualization System

**File:** `src/visualization/map_generator.py`

**Features:**
- Heatmap generation with customizable colormaps
- Contour plots and 3D surface plots
- Statistics overlays
- Multiple export formats (PNG, JSON, CSV, NPZ)
- Animated scan progress (GIF)

### 5. REST API Endpoints

**File:** `src/api/scan.py`

**Endpoints:**
- `POST /api/ml/scan/start` - Start a new scan
- `GET /api/ml/scan/status` - Get scan progress
- `POST /api/ml/scan/pause` - Pause current scan
- `POST /api/ml/scan/resume` - Resume paused scan
- `POST /api/ml/scan/cancel` - Cancel current scan
- `GET /api/ml/scan/result/heatmap` - Get heatmap image
- `GET /api/ml/scan/result/data` - Get raw scan data
- `GET /api/ml/scan/hardware/status` - Hardware status
- `POST /api/ml/scan/hardware/home` - Home the stage

### 6. Demo Frontend

**File:** `static/index.html`

**Features:**
- Interactive scan parameter configuration
- Real-time progress monitoring
- Live heatmap visualization
- Hardware control interface
- Statistics display

## Usage Guide

### Starting the Service

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Access Demo Frontend:**
   Open `http://localhost:8001/static/index.html` in your browser

### API Usage Examples

#### Start a Scan

```python
import requests

scan_params = {
    "x_start": 0.0,
    "y_start": 0.0,
    "x_end": 5.0,
    "y_end": 5.0,
    "step_x": 0.5,
    "step_y": 0.5,
    "integration_time": 0.1,
    "model_id": "default",
    "serpentine": True,
    "batch_size": 1
}

response = requests.post(
    "http://localhost:8001/api/ml/scan/start",
    json=scan_params
)

scan_id = response.json()["scan_id"]
```

#### Monitor Progress

```python
import time

while True:
    status = requests.get("http://localhost:8001/api/ml/scan/status").json()
    
    print(f"Status: {status['status']}")
    print(f"Progress: {status['progress']:.1%}")
    
    if status['status'] in ['completed', 'error', 'cancelled']:
        break
    
    time.sleep(2)
```

#### Get Results

```python
# Get heatmap image
heatmap_response = requests.get(
    "http://localhost:8001/api/ml/scan/result/heatmap?format=png"
)

with open("purity_heatmap.png", "wb") as f:
    f.write(heatmap_response.content)

# Get raw data
data_response = requests.get(
    "http://localhost:8001/api/ml/scan/result/data?format=json"
)

scan_data = data_response.json()
```

### Python SDK Usage

```python
from src.core.scan_orchestrator import ScanOrchestrator, ScanParameters
from src.hardware.stage_controller import StageController, StageConfig
from src.hardware.spectrometer import SpectrometerController
from src.visualization.map_generator import MapGenerator

# Initialize hardware
stage = StageController(StageConfig(x_max_mm=50.0, y_max_mm=50.0))
spectrometer = SpectrometerController()

# Create orchestrator
orchestrator = ScanOrchestrator(stage, spectrometer)

# Define scan parameters
params = ScanParameters(
    x_start=0.0, y_start=0.0,
    x_end=10.0, y_end=10.0,
    step_x=1.0, step_y=1.0,
    integration_time=0.1
)

# Run scan
result = await orchestrator.start_scan(params)

# Generate visualization
generator = MapGenerator()
heatmap_bytes = generator.generate_heatmap(
    result.grid,
    result.x_positions,
    result.y_positions,
    output_path="scan_result.png"
)
```

## Configuration

### Scan Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `x_start` | float | Start X position (mm) | 0.0 |
| `y_start` | float | Start Y position (mm) | 0.0 |
| `x_end` | float | End X position (mm) | Required |
| `y_end` | float | End Y position (mm) | Required |
| `step_x` | float | X step size (mm) | 0.5 |
| `step_y` | float | Y step size (mm) | 0.5 |
| `integration_time` | float | Spectrometer integration time (s) | 0.1 |
| `model_id` | string | ML model to use | "default" |
| `serpentine` | boolean | Use serpentine scanning pattern | true |
| `batch_size` | integer | Batch size for ML inference | 1 |

### Hardware Configuration

#### Stage Controller
```python
StageConfig(
    x_max_mm=50.0,          # Maximum X travel (mm)
    y_max_mm=50.0,          # Maximum Y travel (mm)
    home_pos=(0.0, 0.0),    # Home position
    max_speed_mm_s=10.0,    # Maximum speed (mm/s)
    acceleration_mm_s2=50.0 # Acceleration (mm/s²)
)
```

#### Spectrometer Controller
```python
SpectrometerConfig(
    wavelength_min=400.0,        # Minimum wavelength (nm)
    wavelength_max=1800.0,       # Maximum wavelength (nm)
    num_pixels=1024,             # Number of pixels
    integration_time_min=0.001,  # Minimum integration time (s)
    integration_time_max=10.0,   # Maximum integration time (s)
    default_integration_time=0.1 # Default integration time (s)
)
```

### Visualization Configuration

```python
HeatmapConfig(
    figsize=(10, 8),           # Figure size (inches)
    dpi=150,                   # Resolution (DPI)
    cmap='viridis',            # Colormap
    interpolation='nearest',   # Interpolation method
    show_colorbar=True,        # Show colorbar
    title="Purity Scan",       # Plot title
    vmin=None,                 # Minimum value for colormap
    vmax=None                  # Maximum value for colormap
)
```

## Performance Optimization

### Model Warmup
- Automatic model warmup on startup
- Reduces first-inference latency
- Supports PyTorch, PLSR, and mock models

### Batch Processing
- Configurable batch sizes for ML inference
- Reduces per-sample overhead
- Improves throughput for large scans

### TorchScript Optimization
- Automatic TorchScript tracing for PyTorch models
- Improved inference performance
- Fallback to regular PyTorch if tracing fails

### Memory Management
- Efficient numpy array handling
- Streaming data processing
- Configurable worker threads

## Safety Features

### Hardware Safety
- Movement bounds checking
- Emergency stop functionality
- Homing requirement before movement
- Connection status monitoring

### Scan Safety
- Parameter validation
- Progress monitoring
- Error recovery
- Graceful cancellation

### Data Integrity
- Comprehensive error logging
- Data validation
- Backup and recovery
- Export verification

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_stage_controller.py
pytest tests/test_scan_orchestrator.py
pytest tests/test_visualization.py

# Run with coverage
pytest --cov=src tests/
```

## Hardware Integration

### Real Hardware Setup

To integrate with real hardware, replace the mock implementations:

1. **Stage Controller:**
   - Implement serial/USB communication
   - Add vendor-specific SDK calls
   - Handle hardware-specific error codes

2. **Spectrometer:**
   - Integrate with spectrometer SDK (Ocean Optics, Andor, etc.)
   - Implement proper acquisition timing
   - Handle hardware calibration

### Example Real Hardware Integration

```python
# Example for Ocean Optics spectrometer
import seabreeze.spectrometers as sb

class RealSpectrometerController(SpectrometerController):
    def connect(self, device_id=None):
        self.spec = sb.Spectrometer.from_serial_number(device_id)
        self.is_connected = True
    
    def read_spectrum(self, integration_time=None):
        if integration_time:
            self.spec.integration_time_micros(int(integration_time * 1e6))
        
        wavelengths = self.spec.wavelengths()
        intensities = self.spec.intensities()
        
        return wavelengths, intensities
```

## Troubleshooting

### Common Issues

1. **Hardware Connection Errors:**
   - Check USB/serial connections
   - Verify driver installation
   - Test hardware independently

2. **Scan Failures:**
   - Verify stage limits
   - Check model loading
   - Review error logs

3. **Performance Issues:**
   - Reduce batch size
   - Optimize integration time
   - Check system resources

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

Check log files for detailed error information:
- Application logs: Check console output
- Hardware logs: Check hardware-specific logs
- ML inference logs: Check model loading and prediction logs

## Future Enhancements

### Planned Features
- WebSocket streaming for real-time updates
- Advanced scan patterns (spiral, adaptive)
- Multi-model ensemble predictions
- Cloud storage integration
- Advanced analytics and reporting

### Hardware Expansion
- Support for additional spectrometer vendors
- Multi-axis stage control (Z-axis)
- Temperature and environmental monitoring
- Automated sample handling

### Performance Improvements
- GPU acceleration for ML inference
- Distributed scanning across multiple devices
- Advanced caching and prefetching
- Real-time data compression

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Purity Vision Lab system. See the main project license for details.
