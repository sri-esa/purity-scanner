#!/usr/bin/env python3
"""
Generate fake Raman spectroscopy data for testing and development
"""

import numpy as np
import json
from pathlib import Path
import argparse

def generate_raman_spectrum(purity_level: float = 0.9, noise_level: float = 0.05) -> tuple:
    """
    Generate a synthetic Raman spectrum
    
    Args:
        purity_level: Purity level (0-1)
        noise_level: Amount of noise to add
    
    Returns:
        Tuple of (wavelengths, intensities)
    """
    # Standard Raman shift range (cm-1)
    wavelengths = np.linspace(200, 3500, 1024)
    
    # Base spectrum with characteristic peaks
    intensities = np.zeros_like(wavelengths)
    
    # Add main compound peaks (higher purity = stronger peaks)
    main_peaks = [500, 1000, 1500, 2000, 2500]
    for peak in main_peaks:
        idx = np.argmin(np.abs(wavelengths - peak))
        width = 50
        peak_intensity = purity_level * np.random.uniform(0.7, 1.0)
        
        # Gaussian peak
        peak_range = slice(max(0, idx-width), min(len(wavelengths), idx+width))
        x = wavelengths[peak_range]
        intensities[peak_range] += peak_intensity * np.exp(-0.5 * ((x - peak) / 20)**2)
    
    # Add impurity peaks (lower purity = more impurity peaks)
    impurity_level = 1 - purity_level
    num_impurities = int(impurity_level * 10)
    
    for _ in range(num_impurities):
        peak_pos = np.random.uniform(300, 3000)
        idx = np.argmin(np.abs(wavelengths - peak_pos))
        width = 30
        peak_intensity = impurity_level * np.random.uniform(0.2, 0.6)
        
        peak_range = slice(max(0, idx-width), min(len(wavelengths), idx+width))
        x = wavelengths[peak_range]
        intensities[peak_range] += peak_intensity * np.exp(-0.5 * ((x - peak_pos) / 15)**2)
    
    # Add baseline
    baseline = 0.1 + 0.05 * np.sin(wavelengths / 1000)
    intensities += baseline
    
    # Add noise
    noise = np.random.normal(0, noise_level, len(intensities))
    intensities += noise
    
    # Ensure non-negative
    intensities = np.maximum(intensities, 0)
    
    return wavelengths, intensities

def generate_dataset(num_samples: int = 1000, output_dir: str = "data"):
    """
    Generate a dataset of synthetic spectra
    
    Args:
        num_samples: Number of samples to generate
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    spectra = []
    labels = []
    metadata = []
    
    print(f"Generating {num_samples} synthetic spectra...")
    
    for i in range(num_samples):
        # Random purity level
        purity = np.random.uniform(0.6, 0.99)
        noise = np.random.uniform(0.01, 0.1)
        
        wavelengths, intensities = generate_raman_spectrum(purity, noise)
        
        spectra.append(intensities)
        labels.append(purity * 100)  # Convert to percentage
        metadata.append({
            "sample_id": f"synthetic_{i:04d}",
            "purity_percentage": purity * 100,
            "noise_level": noise,
            "wavelength_range": [float(wavelengths.min()), float(wavelengths.max())],
            "num_points": len(wavelengths)
        })
        
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{num_samples} samples")
    
    # Convert to numpy arrays
    spectra = np.array(spectra)
    labels = np.array(labels)
    
    # Save data
    np.save(output_path / "train_spectra.npy", spectra)
    np.save(output_path / "train_labels.npy", labels)
    np.save(output_path / "wavelengths.npy", wavelengths)
    
    # Save metadata
    with open(output_path / "metadata.json", 'w') as f:
        json.dump({
            "num_samples": num_samples,
            "wavelength_points": len(wavelengths),
            "purity_range": [float(labels.min()), float(labels.max())],
            "samples": metadata
        }, f, indent=2)
    
    print(f"Dataset saved to {output_path}")
    print(f"Spectra shape: {spectra.shape}")
    print(f"Labels range: {labels.min():.2f} - {labels.max():.2f}%")

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Raman spectroscopy data")
    parser.add_argument("--samples", type=int, default=1000, help="Number of samples to generate")
    parser.add_argument("--output", type=str, default="data", help="Output directory")
    
    args = parser.parse_args()
    
    generate_dataset(args.samples, args.output)

if __name__ == "__main__":
    main()
