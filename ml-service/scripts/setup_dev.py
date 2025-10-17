#!/usr/bin/env python3
"""
Development setup script for ML service
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(cmd, cwd=None, check=True):
    """Run shell command"""
    logger.info(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"Error: {result.stderr}")
        sys.exit(1)
    
    return result

def setup_environment():
    """Setup Python virtual environment"""
    logger.info("Setting up Python virtual environment...")
    
    # Create venv if it doesn't exist
    if not Path("venv").exists():
        run_command(f"{sys.executable} -m venv venv")
        logger.info("✅ Virtual environment created")
    else:
        logger.info("✅ Virtual environment already exists")
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        activate_script = "venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    logger.info("Installing Python dependencies...")
    run_command(f"{pip_cmd} install --upgrade pip")
    run_command(f"{pip_cmd} install -r requirements.txt")
    logger.info("✅ Dependencies installed")
    
    return activate_script

def setup_directories():
    """Create necessary directories"""
    logger.info("Creating directory structure...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "models/baseline",
        "models/plsr",
        "logs/api",
        "logs/training",
        "logs/evaluation"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created {directory}")

def setup_environment_file():
    """Setup .env file from template"""
    logger.info("Setting up environment file...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        logger.info("✅ Created .env from .env.example")
    elif env_file.exists():
        logger.info("✅ .env file already exists")
    else:
        logger.warning("⚠️ No .env.example found, creating basic .env")
        
        basic_env = """# ML Service Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Model Settings
MODEL_TYPE=mock
SPECTRUM_LENGTH=1024

# API Settings
API_HOST=0.0.0.0
API_PORT=8001
WORKERS=1

# Device
DEVICE=cpu
"""
        with open(env_file, 'w') as f:
            f.write(basic_env)

def generate_test_data():
    """Generate synthetic test data"""
    logger.info("Generating synthetic test data...")
    
    try:
        run_command(f"{sys.executable} scripts/generate_fake_data.py --samples 500 --output data")
        logger.info("✅ Test data generated")
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate test data: {e}")

def create_gitkeep_files():
    """Create .gitkeep files for empty directories"""
    logger.info("Creating .gitkeep files...")
    
    gitkeep_dirs = [
        "data/raw",
        "data/processed",
        "logs/api", 
        "logs/training",
        "logs/evaluation"
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_file = Path(directory) / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.touch()
            logger.info(f"✅ Created {gitkeep_file}")

def setup_pre_commit_hooks():
    """Setup pre-commit hooks for code quality"""
    logger.info("Setting up pre-commit hooks...")
    
    try:
        # Install pre-commit if available
        run_command("pip install pre-commit", check=False)
        
        # Create .pre-commit-config.yaml if it doesn't exist
        pre_commit_config = Path(".pre-commit-config.yaml")
        if not pre_commit_config.exists():
            config_content = """repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
"""
            with open(pre_commit_config, 'w') as f:
                f.write(config_content)
        
        # Install hooks
        run_command("pre-commit install", check=False)
        logger.info("✅ Pre-commit hooks installed")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to setup pre-commit hooks: {e}")

def verify_setup():
    """Verify the setup by running basic tests"""
    logger.info("Verifying setup...")
    
    try:
        # Test imports
        run_command(f"{sys.executable} -c 'import fastapi, torch, numpy, sklearn; print(\"All imports successful\")'")
        logger.info("✅ Core dependencies verified")
        
        # Test FastAPI app startup (dry run)
        run_command(f"{sys.executable} -c 'from main import app; print(\"FastAPI app created successfully\")'")
        logger.info("✅ FastAPI app verification passed")
        
    except Exception as e:
        logger.error(f"❌ Setup verification failed: {e}")
        return False
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    logger.info("\n🎉 Setup completed successfully!")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    
    if os.name == 'nt':  # Windows
        print("1. Activate virtual environment:")
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("1. Activate virtual environment:")
        print("   source venv/bin/activate")
    
    print("\n2. Start the ML service:")
    print("   uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
    
    print("\n3. Test the service:")
    print("   curl http://localhost:8001/api/ml/health")
    
    print("\n4. Run tests:")
    print("   pytest tests/ -v")
    
    print("\n5. Generate more training data (optional):")
    print("   python scripts/generate_fake_data.py --samples 1000")
    
    print("\n6. Train a model (optional):")
    print("   python scripts/train_baseline.py --epochs 10")
    
    print("\n" + "="*60)
    print("For more information, see:")
    print("- README.md")
    print("- docs/API.md")
    print("- docs/DEPLOYMENT.md")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Setup ML service development environment")
    parser.add_argument("--skip-data", action="store_true", help="Skip test data generation")
    parser.add_argument("--skip-hooks", action="store_true", help="Skip pre-commit hooks setup")
    
    args = parser.parse_args()
    
    logger.info("🚀 Setting up PurityScan ML Service development environment...")
    
    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    try:
        # Setup steps
        setup_directories()
        setup_environment_file()
        create_gitkeep_files()
        activate_script = setup_environment()
        
        if not args.skip_data:
            generate_test_data()
        
        if not args.skip_hooks:
            setup_pre_commit_hooks()
        
        # Verify setup
        if verify_setup():
            print_next_steps()
        else:
            logger.error("❌ Setup verification failed. Please check the logs above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
