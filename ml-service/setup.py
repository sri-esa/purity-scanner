#!/usr/bin/env python3
"""
Quick setup script for ML service
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="purityscan-ml-service",
    version="1.0.0",
    author="PurityScan Team",
    author_email="team@purityscan.com",
    description="Machine Learning microservice for Raman spectroscopy purity analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/purity-vision-lab",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "pre-commit>=3.0.0",
        ],
        "gpu": [
            "torch[cuda]>=2.0.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "matplotlib>=3.8.0",
            "seaborn>=0.13.0",
            "plotly>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "purity-ml-serve=main:main",
            "purity-ml-train=scripts.train_baseline:main",
            "purity-ml-evaluate=scripts.evaluate_model:main",
            "purity-ml-setup=scripts.setup_dev:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md"],
    },
)
