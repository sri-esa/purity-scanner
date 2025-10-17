#!/usr/bin/env python3
"""
Training script for baseline HuggingFace model
"""

import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import json
from pathlib import Path
import argparse
import logging
from src.models.huggingface_model import PurityTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(data_dir: str):
    """Load training data"""
    data_path = Path(data_dir)
    
    spectra = np.load(data_path / "train_spectra.npy")
    labels = np.load(data_path / "train_labels.npy")
    
    logger.info(f"Loaded {len(spectra)} samples")
    logger.info(f"Spectrum shape: {spectra.shape}")
    logger.info(f"Label range: {labels.min():.2f} - {labels.max():.2f}")
    
    return spectra, labels

def create_dataloaders(spectra, labels, batch_size=32, test_size=0.2):
    """Create train/validation dataloaders"""
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        spectra, labels, test_size=test_size, random_state=42
    )
    
    # Convert to tensors
    X_train = torch.FloatTensor(X_train)
    X_val = torch.FloatTensor(X_val)
    y_train = torch.FloatTensor(y_train).unsqueeze(1)  # Add dimension for regression
    y_val = torch.FloatTensor(y_val).unsqueeze(1)
    
    # Create datasets
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader

def train_model(model, train_loader, val_loader, epochs=50, lr=1e-4, device='cpu'):
    """Train the model"""
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)
    
    best_val_loss = float('inf')
    train_losses = []
    val_losses = []
    
    logger.info(f"Starting training for {epochs} epochs on {device}")
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        predictions = []
        targets = []
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                val_loss += criterion(output, target).item()
                
                predictions.extend(output.cpu().numpy())
                targets.extend(target.cpu().numpy())
        
        # Calculate metrics
        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        
        predictions = np.array(predictions).flatten()
        targets = np.array(targets).flatten()
        
        r2 = r2_score(targets, predictions)
        rmse = np.sqrt(mean_squared_error(targets, predictions))
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), 'models/baseline/best_model.pth')
        
        # Logging
        if (epoch + 1) % 5 == 0:
            logger.info(f'Epoch {epoch+1}/{epochs}:')
            logger.info(f'  Train Loss: {train_loss:.4f}')
            logger.info(f'  Val Loss: {val_loss:.4f}')
            logger.info(f'  Val R²: {r2:.4f}')
            logger.info(f'  Val RMSE: {rmse:.4f}')
    
    return train_losses, val_losses

def save_model_info(model, train_losses, val_losses, output_dir):
    """Save model information and training history"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Model info
    model_info = {
        "name": "PurityScan Baseline",
        "version": "1.0.0",
        "architecture": "HuggingFace Transformer",
        "input_size": model.spectrum_length,
        "accuracy": float(1 - min(val_losses)),  # Approximate accuracy
        "description": "HuggingFace transformer model for purity analysis",
        "training_history": {
            "train_losses": [float(x) for x in train_losses],
            "val_losses": [float(x) for x in val_losses],
            "epochs": len(train_losses)
        }
    }
    
    with open(output_path / "model_info.json", 'w') as f:
        json.dump(model_info, f, indent=2)
    
    logger.info(f"Model info saved to {output_path / 'model_info.json'}")

def main():
    parser = argparse.ArgumentParser(description="Train baseline HuggingFace model")
    parser.add_argument("--data", type=str, default="data", help="Data directory")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu/cuda)")
    parser.add_argument("--output", type=str, default="models/baseline", help="Output directory")
    
    args = parser.parse_args()
    
    # Check device
    device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA not available, using CPU")
        device = "cpu"
    
    # Load data
    spectra, labels = load_data(args.data)
    
    # Create dataloaders
    train_loader, val_loader = create_dataloaders(
        spectra, labels, batch_size=args.batch_size
    )
    
    # Create model
    model = PurityTransformer(spectrum_length=spectra.shape[1])
    
    # Train model
    train_losses, val_losses = train_model(
        model, train_loader, val_loader, 
        epochs=args.epochs, lr=args.lr, device=device
    )
    
    # Save final model
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    torch.save(model.state_dict(), output_path / "purityscan_huggingface.pth")
    
    # Save model info
    save_model_info(model, train_losses, val_losses, args.output)
    
    logger.info("Training completed successfully!")

if __name__ == "__main__":
    main()
