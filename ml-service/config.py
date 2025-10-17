import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Model
    MODEL_TYPE = os.getenv("MODEL_TYPE", "baseline")
    MODEL_PATH = os.getenv("MODEL_PATH", "models/baseline/purityscan_huggingface.pth")
    SPECTRUM_LENGTH = int(os.getenv("SPECTRUM_LENGTH", "1024"))
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8001"))
    WORKERS = int(os.getenv("WORKERS", "2"))
    
    # Device
    DEVICE = os.getenv("DEVICE", "cpu")
    
    # Validation
    MIN_SPECTRUM_LENGTH = 100
    MAX_SPECTRUM_LENGTH = 5000

settings = Settings()
