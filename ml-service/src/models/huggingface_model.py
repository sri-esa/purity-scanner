import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig
from typing import Optional

class PurityTransformer(nn.Module):
    """
    HuggingFace transformer-based model for purity analysis
    """
    
    def __init__(self, 
                 model_name: str = "distilbert-base-uncased",
                 spectrum_length: int = 1024,
                 hidden_dim: int = 256,
                 num_classes: int = 1):
        super().__init__()
        
        self.spectrum_length = spectrum_length
        self.hidden_dim = hidden_dim
        
        # Load pre-trained transformer (we'll adapt it for spectral data)
        self.config = AutoConfig.from_pretrained(model_name)
        self.transformer = AutoModel.from_pretrained(model_name)
        
        # Freeze transformer layers initially
        for param in self.transformer.parameters():
            param.requires_grad = False
        
        # Spectrum embedding layer
        self.spectrum_embedding = nn.Linear(spectrum_length, self.config.hidden_size)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(self.config.hidden_size, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, num_classes)
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize custom layer weights"""
        for module in [self.spectrum_embedding, self.classifier]:
            if isinstance(module, nn.Linear):
                torch.nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    torch.nn.init.constant_(module.bias, 0)
    
    def forward(self, spectrum: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            spectrum: Input spectrum tensor [batch_size, spectrum_length]
        
        Returns:
            Purity predictions [batch_size, 1]
        """
        batch_size = spectrum.shape[0]
        
        # Embed spectrum to transformer hidden size
        embedded = self.spectrum_embedding(spectrum)  # [batch_size, hidden_size]
        
        # Add sequence dimension for transformer
        embedded = embedded.unsqueeze(1)  # [batch_size, 1, hidden_size]
        
        # Create attention mask (all ones since we have single sequence)
        attention_mask = torch.ones(batch_size, 1, device=spectrum.device)
        
        # Pass through transformer
        transformer_output = self.transformer(
            inputs_embeds=embedded,
            attention_mask=attention_mask
        )
        
        # Get pooled output
        pooled_output = transformer_output.last_hidden_state.mean(dim=1)  # [batch_size, hidden_size]
        
        # Classification
        output = self.classifier(pooled_output)  # [batch_size, 1]
        
        return output
    
    def unfreeze_transformer(self, num_layers: Optional[int] = None):
        """
        Unfreeze transformer layers for fine-tuning
        
        Args:
            num_layers: Number of top layers to unfreeze. If None, unfreeze all
        """
        if num_layers is None:
            # Unfreeze all transformer parameters
            for param in self.transformer.parameters():
                param.requires_grad = True
        else:
            # Unfreeze only the top num_layers
            layers = list(self.transformer.encoder.layer)
            for layer in layers[-num_layers:]:
                for param in layer.parameters():
                    param.requires_grad = True

class SimpleCNN(nn.Module):
    """
    Simple CNN model for spectrum analysis
    """
    
    def __init__(self, spectrum_length: int = 1024, num_classes: int = 1):
        super().__init__()
        
        self.spectrum_length = spectrum_length
        
        # 1D CNN layers
        self.conv_layers = nn.Sequential(
            # First conv block
            nn.Conv1d(1, 32, kernel_size=7, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            
            # Second conv block
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            
            # Third conv block
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2),
            
            # Fourth conv block
            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(16)  # Adaptive pooling to fixed size
        )
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 16, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input spectrum [batch_size, spectrum_length]
        
        Returns:
            Predictions [batch_size, num_classes]
        """
        # Add channel dimension
        x = x.unsqueeze(1)  # [batch_size, 1, spectrum_length]
        
        # Convolutional layers
        x = self.conv_layers(x)
        
        # Fully connected layers
        x = self.fc_layers(x)
        
        return x

def create_model(model_type: str = "transformer", **kwargs) -> nn.Module:
    """
    Factory function to create models
    
    Args:
        model_type: Type of model to create
        **kwargs: Model-specific arguments
    
    Returns:
        Initialized model
    """
    if model_type == "transformer":
        return PurityTransformer(**kwargs)
    elif model_type == "cnn":
        return SimpleCNN(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
