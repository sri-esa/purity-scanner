#!/usr/bin/env python3
"""
Model evaluation script
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from pathlib import Path
import argparse
import json
import logging
from src.core.model_loader import ModelLoader
from src.core.inference import InferenceEngine
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def evaluate_model(test_data_path: str, model_type: str = "baseline"):
    """
    Evaluate model performance on test data
    
    Args:
        test_data_path: Path to test data
        model_type: Type of model to evaluate
    """
    # Load test data
    data_path = Path(test_data_path)
    
    if not (data_path / "train_spectra.npy").exists():
        logger.error(f"Test data not found at {test_data_path}")
        return
    
    spectra = np.load(data_path / "train_spectra.npy")
    true_labels = np.load(data_path / "train_labels.npy")
    wavelengths = np.load(data_path / "wavelengths.npy")
    
    logger.info(f"Loaded {len(spectra)} test samples")
    
    # Initialize model
    await ModelLoader.initialize()
    
    if not ModelLoader.is_loaded():
        logger.error("Failed to load model")
        return
    
    # Make predictions
    predictions = []
    confidences = []
    processing_times = []
    
    logger.info("Making predictions...")
    
    for i, spectrum in enumerate(spectra):
        if i % 100 == 0:
            logger.info(f"Processing sample {i+1}/{len(spectra)}")
        
        try:
            # Convert spectrum to wavelengths/intensities format
            result = await InferenceEngine.predict(
                wavelengths=wavelengths.tolist(),
                intensities=spectrum.tolist()
            )
            
            predictions.append(result["purity_percentage"])
            confidences.append(result["confidence_score"])
            
        except Exception as e:
            logger.error(f"Prediction failed for sample {i}: {e}")
            predictions.append(np.nan)
            confidences.append(0.0)
    
    predictions = np.array(predictions)
    confidences = np.array(confidences)
    
    # Remove failed predictions
    valid_mask = ~np.isnan(predictions)
    predictions = predictions[valid_mask]
    true_labels = true_labels[valid_mask]
    confidences = confidences[valid_mask]
    
    logger.info(f"Successfully predicted {len(predictions)} samples")
    
    # Calculate metrics
    metrics = calculate_metrics(true_labels, predictions, confidences)
    
    # Generate plots
    generate_evaluation_plots(true_labels, predictions, confidences, model_type)
    
    # Save results
    save_evaluation_results(metrics, model_type)
    
    return metrics

def calculate_metrics(true_labels, predictions, confidences):
    """Calculate evaluation metrics"""
    metrics = {
        "mse": float(mean_squared_error(true_labels, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(true_labels, predictions))),
        "mae": float(mean_absolute_error(true_labels, predictions)),
        "r2": float(r2_score(true_labels, predictions)),
        "mean_confidence": float(np.mean(confidences)),
        "std_confidence": float(np.std(confidences)),
        "num_samples": len(predictions)
    }
    
    # Additional metrics
    residuals = predictions - true_labels
    metrics.update({
        "mean_residual": float(np.mean(residuals)),
        "std_residual": float(np.std(residuals)),
        "max_error": float(np.max(np.abs(residuals))),
        "accuracy_5pct": float(np.mean(np.abs(residuals) < 5.0)),  # Within 5% accuracy
        "accuracy_10pct": float(np.mean(np.abs(residuals) < 10.0))  # Within 10% accuracy
    })
    
    logger.info("Evaluation Metrics:")
    logger.info(f"  RMSE: {metrics['rmse']:.3f}")
    logger.info(f"  MAE: {metrics['mae']:.3f}")
    logger.info(f"  R²: {metrics['r2']:.3f}")
    logger.info(f"  Mean Confidence: {metrics['mean_confidence']:.3f}")
    logger.info(f"  Accuracy (±5%): {metrics['accuracy_5pct']*100:.1f}%")
    logger.info(f"  Accuracy (±10%): {metrics['accuracy_10pct']*100:.1f}%")
    
    return metrics

def generate_evaluation_plots(true_labels, predictions, confidences, model_type):
    """Generate evaluation plots"""
    output_dir = Path("logs") / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
    
    # 1. Prediction vs True scatter plot
    plt.figure(figsize=(10, 8))
    
    plt.subplot(2, 2, 1)
    plt.scatter(true_labels, predictions, alpha=0.6, c=confidences, cmap='viridis')
    plt.plot([true_labels.min(), true_labels.max()], 
             [true_labels.min(), true_labels.max()], 'r--', lw=2)
    plt.xlabel('True Purity (%)')
    plt.ylabel('Predicted Purity (%)')
    plt.title('Predictions vs True Values')
    plt.colorbar(label='Confidence')
    
    # 2. Residuals plot
    plt.subplot(2, 2, 2)
    residuals = predictions - true_labels
    plt.scatter(true_labels, residuals, alpha=0.6)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('True Purity (%)')
    plt.ylabel('Residuals (%)')
    plt.title('Residuals vs True Values')
    
    # 3. Confidence distribution
    plt.subplot(2, 2, 3)
    plt.hist(confidences, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('Confidence Score')
    plt.ylabel('Frequency')
    plt.title('Confidence Score Distribution')
    
    # 4. Error vs Confidence
    plt.subplot(2, 2, 4)
    errors = np.abs(residuals)
    plt.scatter(confidences, errors, alpha=0.6)
    plt.xlabel('Confidence Score')
    plt.ylabel('Absolute Error (%)')
    plt.title('Error vs Confidence')
    
    plt.tight_layout()
    plt.savefig(output_dir / f"{model_type}_evaluation.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Additional detailed plots
    plt.figure(figsize=(12, 4))
    
    # Error histogram
    plt.subplot(1, 3, 1)
    plt.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('Prediction Error (%)')
    plt.ylabel('Frequency')
    plt.title('Error Distribution')
    plt.axvline(x=0, color='r', linestyle='--')
    
    # Q-Q plot for residuals
    plt.subplot(1, 3, 2)
    from scipy import stats
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title('Q-Q Plot of Residuals')
    
    # Confidence vs accuracy
    plt.subplot(1, 3, 3)
    # Bin by confidence and calculate accuracy in each bin
    conf_bins = np.linspace(0, 1, 11)
    bin_centers = (conf_bins[:-1] + conf_bins[1:]) / 2
    bin_accuracies = []
    
    for i in range(len(conf_bins) - 1):
        mask = (confidences >= conf_bins[i]) & (confidences < conf_bins[i+1])
        if np.sum(mask) > 0:
            bin_accuracy = np.mean(np.abs(residuals[mask]) < 5.0)  # Within 5%
            bin_accuracies.append(bin_accuracy)
        else:
            bin_accuracies.append(0)
    
    plt.bar(bin_centers, bin_accuracies, width=0.08, alpha=0.7, edgecolor='black')
    plt.xlabel('Confidence Score')
    plt.ylabel('Accuracy (±5%)')
    plt.title('Accuracy vs Confidence')
    plt.ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(output_dir / f"{model_type}_detailed_evaluation.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Evaluation plots saved to {output_dir}")

def save_evaluation_results(metrics, model_type):
    """Save evaluation results to JSON"""
    output_dir = Path("logs") / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "model_type": model_type,
        "evaluation_date": str(np.datetime64('now')),
        "metrics": metrics
    }
    
    output_file = output_dir / f"{model_type}_evaluation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Evaluation results saved to {output_file}")

async def main():
    parser = argparse.ArgumentParser(description="Evaluate ML model")
    parser.add_argument("--data", type=str, default="data", help="Test data directory")
    parser.add_argument("--model", type=str, default="baseline", help="Model type to evaluate")
    
    args = parser.parse_args()
    
    metrics = await evaluate_model(args.data, args.model)
    
    if metrics:
        logger.info("Evaluation completed successfully!")
    else:
        logger.error("Evaluation failed!")

if __name__ == "__main__":
    asyncio.run(main())
