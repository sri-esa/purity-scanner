import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class CNN1D(nn.Module):
    """
    1D Convolutional Neural Network for Raman spectrum purity analysis
    
    Architecture:
    - Input: 1D spectrum (1024 points)
    - Conv1D layers with batch normalization and dropout
    - Global average pooling
    - Dense layers for regression output
    """
    
    def __init__(self, input_size: int = 1024, num_classes: int = 1, dropout_rate: float = 0.3):
        super(CNN1D, self).__init__()
        
        self.input_size = input_size
        self.num_classes = num_classes
        
        # Convolutional layers
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=64, kernel_size=7, padding=3)
        self.bn1 = nn.BatchNorm1d(64)
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(128)
        self.pool2 = nn.MaxPool1d(kernel_size=2)
        
        self.conv3 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(256)
        self.pool3 = nn.MaxPool1d(kernel_size=2)
        
        self.conv4 = nn.Conv1d(in_channels=256, out_channels=512, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm1d(512)
        
        # Global average pooling
        self.global_avg_pool = nn.AdaptiveAvgPool1d(1)
        
        # Dense layers
        self.dropout = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(512, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        
        # Output layers
        self.purity_head = nn.Linear(64, 1)  # Purity percentage (0-100)
        self.confidence_head = nn.Linear(64, 1)  # Confidence score (0-1)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize model weights using Xavier/He initialization"""
        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass through the network
        
        Args:
            x: Input tensor of shape (batch_size, input_size) or (batch_size, 1, input_size)
        
        Returns:
            Dictionary with purity and confidence predictions
        """
        # Ensure input has correct shape (batch_size, 1, input_size)
        if x.dim() == 2:
            x = x.unsqueeze(1)  # Add channel dimension
        
        # Convolutional layers with ReLU activation and pooling
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = F.relu(self.bn4(self.conv4(x)))
        
        # Global average pooling
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)  # Flatten
        
        # Dense layers with dropout
        x = F.relu(self.fc1(self.dropout(x)))
        x = F.relu(self.fc2(self.dropout(x)))
        features = F.relu(self.fc3(self.dropout(x)))
        
        # Output predictions
        purity = torch.sigmoid(self.purity_head(features)) * 100  # Scale to 0-100%
        confidence = torch.sigmoid(self.confidence_head(features))  # 0-1 range
        
        return {
            'purity': purity,
            'confidence': confidence,
            'features': features
        }
    
    def predict_purity(self, spectrum: np.ndarray) -> Tuple[float, float]:
        """
        Predict purity from a single spectrum
        
        Args:
            spectrum: 1D numpy array of spectrum intensities
        
        Returns:
            Tuple of (purity_percentage, confidence_score)
        """
        self.eval()
        
        with torch.no_grad():
            # Convert to tensor and add batch dimension
            if isinstance(spectrum, np.ndarray):
                spectrum_tensor = torch.FloatTensor(spectrum).unsqueeze(0)
            else:
                spectrum_tensor = spectrum.unsqueeze(0)
            
            # Move to device if needed
            if next(self.parameters()).is_cuda:
                spectrum_tensor = spectrum_tensor.cuda()
            
            # Forward pass
            outputs = self.forward(spectrum_tensor)
            
            # Extract predictions
            purity = outputs['purity'].item()
            confidence = outputs['confidence'].item()
            
            return purity, confidence
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model architecture information"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            "name": "1D-CNN Purity Analyzer",
            "type": "cnn_1d",
            "version": "1.0.0",
            "input_size": self.input_size,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "model_size_mb": total_params * 4 / (1024 * 1024),  # Assuming float32
            "architecture": {
                "conv_layers": 4,
                "dense_layers": 3,
                "output_heads": 2,
                "dropout_rate": 0.3,
                "activation": "ReLU",
                "pooling": "MaxPool1d + AdaptiveAvgPool1d"
            }
        }


class MockCNN1D:
    """
    Mock 1D-CNN model for testing when no trained model is available
    """
    
    def __init__(self):
        self.model_info = {
            "name": "Mock 1D-CNN Purity Analyzer",
            "type": "mock_cnn_1d",
            "version": "0.1.0",
            "accuracy": 0.85,
            "description": "Mock CNN model for testing and development"
        }
    
    def predict_purity(self, spectrum: np.ndarray) -> Tuple[float, float]:
        """
        Mock prediction based on spectrum statistics
        
        Args:
            spectrum: 1D numpy array of spectrum intensities
        
        Returns:
            Tuple of (purity_percentage, confidence_score)
        """
        # Simple heuristic based on spectrum properties
        spectrum = np.array(spectrum)
        
        # Calculate basic statistics
        mean_intensity = np.mean(spectrum)
        std_intensity = np.std(spectrum)
        max_intensity = np.max(spectrum)
        
        # Mock purity calculation (higher intensity variation = lower purity)
        noise_ratio = std_intensity / (mean_intensity + 1e-8)
        base_purity = 95 - (noise_ratio * 20)  # Scale noise to purity
        
        # Add some randomness for realism
        purity = np.clip(base_purity + np.random.normal(0, 2), 85, 99)
        
        # Mock confidence (higher for more "typical" spectra)
        signal_to_noise = max_intensity / (std_intensity + 1e-8)
        confidence = np.clip(0.7 + (signal_to_noise / 100), 0.6, 0.95)
        
        return float(purity), float(confidence)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information"""
        return self.model_info
    
    def eval(self):
        """Mock eval method for compatibility"""
        pass


def create_cnn_1d_model(input_size: int = 1024, pretrained: bool = False) -> CNN1D:
    """
    Factory function to create a 1D-CNN model
    
    Args:
        input_size: Size of input spectrum
        pretrained: Whether to load pretrained weights (if available)
    
    Returns:
        CNN1D model instance
    """
    model = CNN1D(input_size=input_size)
    
    if pretrained:
        # TODO: Load pretrained weights when available
        logger.info("Pretrained weights not yet available, using random initialization")
    
    return model


def create_mock_cnn_1d_model() -> MockCNN1D:
    """
    Factory function to create a mock 1D-CNN model
    
    Returns:
        MockCNN1D model instance
    """
    return MockCNN1D()
