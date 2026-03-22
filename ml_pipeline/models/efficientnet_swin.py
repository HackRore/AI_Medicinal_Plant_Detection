"""
EfficientNet + Swin Transformer Hybrid Model
Combines efficient CNNs with attention mechanisms for robust plant identification
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Dict, List, Tuple, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EfficientNetSwinHybrid(nn.Module):
    """
    Hybrid architecture combining:
    - EfficientNetV2-S: Fast feature extraction (backbone)
    - Swin Transformer: Attention-based refinement
    - Confidence scoring layer
    """
    
    def __init__(
        self,
        num_classes: int = 40,
        pretrained: bool = True,
        freeze_backbone: bool = False,
        attention_heads: int = 8,
        transformer_depth: int = 2,
    ):
        """
        Initialize hybrid model
        
        Args:
            num_classes: Number of plant species to classify
            pretrained: Use ImageNet pre-trained weights
            freeze_backbone: Freeze backbone during training
            attention_heads: Number of attention heads
            transformer_depth: Number of transformer blocks
        """
        super().__init__()
        self.num_classes = num_classes
        self.attention_heads = attention_heads
        self.transformer_depth = transformer_depth
        
        # Phase 1: Feature Extraction (EfficientNetV2-S backbone)
        # For now, we use a placeholder that expects a standard backbone
        # In production, use: from timm import create_model
        # self.backbone = create_model('efficientnetv2_s', pretrained=pretrained, num_classes=0)
        self.backbone_hidden_dim = 1280  # EfficientNetV2-S output channels
        
        # Placeholder backbone (in real implementation, use timm)
        self.backbone = self._create_placeholder_backbone()
        
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Phase 2: Multi-Scale Attention Refinement
        self.attention_refiner = MultiScaleAttention(
            input_dim=self.backbone_hidden_dim,
            num_heads=attention_heads,
            depth=transformer_depth
        )
        
        # Phase 3: Confidence Scoring Head
        self.confidence_head = ConfidenceHead(
            input_dim=self.backbone_hidden_dim,
            hidden_dim=512,
            num_classes=num_classes
        )
        
        # Phase 4: Classification Head
        self.classifier = nn.Sequential(
            nn.Linear(self.backbone_hidden_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x: Tensor) -> Dict[str, Tensor]:
        """
        Forward pass with confidence scoring
        
        Args:
            x: Input tensor (B, 3, H, W)
            
        Returns:
            Dict with:
                - logits: Classification logits
                - probabilities: Softmax probabilities
                - confidence: Model confidence scores
                - attention_maps: Attention visualization
        """
        # Extract features
        features = self.backbone(x)  # (B, C, H, W)
        
        # Refine with attention
        refined_features, attention_maps = self.attention_refiner(features)  # (B, C, H, W)
        
        # Global average pooling
        pooled = F.adaptive_avg_pool2d(refined_features, (1, 1))  # (B, C, 1, 1)
        pooled = pooled.flatten(1)  # (B, C)
        
        # Classification
        logits = self.classifier(pooled)  # (B, num_classes)
        probabilities = F.softmax(logits, dim=1)
        
        # Confidence estimation
        confidence = self.confidence_head(pooled)  # (B, num_classes)
        confidence = torch.sigmoid(confidence)
        
        return {
            "logits": logits,
            "probabilities": probabilities,
            "confidence": confidence,
            "attention_maps": attention_maps,
            "features": pooled
        }
    
    def _create_placeholder_backbone(self) -> nn.Module:
        """
        Create placeholder backbone
        In production, replace with: from timm import create_model
        """
        class SimpleBackbone(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 64, 7, stride=2, padding=3)
                self.bn1 = nn.BatchNorm2d(64)
                self.pool1 = nn.MaxPool2d(3, stride=2, padding=1)
                
                self.conv2 = nn.Conv2d(64, 128, 3, stride=1, padding=1)
                self.bn2 = nn.BatchNorm2d(128)
                self.pool2 = nn.AdaptiveAvgPool2d((7, 7))
                
                # Additional layers to reach 1280 channels
                self.conv3 = nn.Conv2d(128, 1280, 1)
            
            def forward(self, x):
                x = self.pool1(self.bn1(F.relu(self.conv1(x))))
                x = self.pool2(self.bn2(F.relu(self.conv2(x))))
                x = self.conv3(x)
                return x
        
        return SimpleBackbone()


class MultiScaleAttention(nn.Module):
    """Multi-scale attention refinement module"""
    
    def __init__(self, input_dim: int, num_heads: int = 8, depth: int = 2):
        super().__init__()
        self.input_dim = input_dim
        self.num_heads = num_heads
        
        self.attention_blocks = nn.ModuleList([
            TransformerBlock(input_dim, num_heads)
            for _ in range(depth)
        ])
    
    def forward(self, x: Tensor) -> Tuple[Tensor, List[Tensor]]:
        """
        Apply multi-scale attention
        
        Args:
            x: Input features (B, C, H, W)
            
        Returns:
            Tuple: (refined_features, attention_maps)
        """
        attention_maps = []
        
        # Reshape for transformer: (B, C, H, W) -> (B, HW, C)
        B, C, H, W = x.shape
        x_flat = x.flatten(2).transpose(1, 2)  # (B, HW, C)
        
        # Apply attention blocks
        for block in self.attention_blocks:
            x_flat, attn = block(x_flat)
            attention_maps.append(attn)
        
        # Reshape back: (B, HW, C) -> (B, C, H, W)
        x_refined = x_flat.transpose(1, 2).reshape(B, C, H, W)
        
        return x_refined, attention_maps


class TransformerBlock(nn.Module):
    """Single transformer block with self-attention and feedforward"""
    
    def __init__(self, dim: int, num_heads: int = 8, mlp_ratio: float = 4.0):
        super().__init__()
        
        # Multi-head self-attention
        self.attention = nn.MultiheadAttention(
            embed_dim=dim,
            num_heads=num_heads,
            batch_first=True,
            dropout=0.1
        )
        
        # Layer normalization and feedforward
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        
        mlp_dim = int(dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(dim, mlp_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(mlp_dim, dim),
            nn.Dropout(0.1)
        )
    
    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        """Forward pass with residual connections"""
        # Self-attention
        x_norm = self.norm1(x)
        attn_out, attn_weights = self.attention(x_norm, x_norm, x_norm)
        x = x + attn_out
        
        # Feedforward
        x_norm = self.norm2(x)
        x = x + self.mlp(x_norm)
        
        return x, attn_weights


class ConfidenceHead(nn.Module):
    """Confidence estimation network"""
    
    def __init__(self, input_dim: int, hidden_dim: int = 512, num_classes: int = 40):
        super().__init__()
        
        self.confidence_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, num_classes)
        )
    
    def forward(self, x: Tensor) -> Tensor:
        """Predict confidence for each class"""
        return self.confidence_net(x)


class HybridModelTrainer:
    """Training utilities for hybrid model"""
    
    def __init__(
        self,
        model: EfficientNetSwinHybrid,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4
    ):
        self.model = model.to(device)
        self.device = device
        
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=100,
            eta_min=1e-6
        )
        
        self.criterion = nn.CrossEntropyLoss()
    
    def train_step(
        self,
        images: Tensor,
        labels: Tensor
    ) -> Dict[str, float]:
        """
        Single training step
        
        Args:
            images: Batch of images (B, 3, H, W)
            labels: Batch of labels (B,)
            
        Returns:
            Dict with loss and metrics
        """
        self.model.train()
        
        images = images.to(self.device)
        labels = labels.to(self.device)
        
        self.optimizer.zero_grad()
        
        # Forward pass
        output = self.model(images)
        logits = output["logits"]
        confidence = output["confidence"]
        
        # Combined loss
        classification_loss = self.criterion(logits, labels)
        confidence_loss = self._confidence_loss(confidence, labels)
        
        total_loss = classification_loss + 0.2 * confidence_loss
        
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        accuracy = (preds == labels).float().mean().item()
        
        return {
            "loss": total_loss.item(),
            "classification_loss": classification_loss.item(),
            "confidence_loss": confidence_loss.item(),
            "accuracy": accuracy
        }
    
    @torch.no_grad()
    def eval_step(self, images: Tensor, labels: Tensor) -> Dict[str, float]:
        """Single evaluation step"""
        self.model.eval()
        
        images = images.to(self.device)
        labels = labels.to(self.device)
        
        output = self.model(images)
        logits = output["logits"]
        
        loss = self.criterion(logits, labels)
        preds = torch.argmax(logits, dim=1)
        accuracy = (preds == labels).float().mean().item()
        
        return {
            "loss": loss.item(),
            "accuracy": accuracy
        }
    
    def _confidence_loss(self, confidence: Tensor, labels: Tensor) -> Tensor:
        """
        Loss to encourage high confidence for correct predictions
        and low confidence for incorrect ones
        """
        one_hot = F.one_hot(labels, num_classes=self.model.num_classes).float()
        
        # Binary cross-entropy on confidence scores
        loss = F.binary_cross_entropy(confidence, one_hot)
        return loss


# Quick inference function
def predict_with_confidence(
    model: EfficientNetSwinHybrid,
    image_tensor: Tensor,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    class_names: Optional[List[str]] = None
) -> Dict:
    """
    Make prediction with confidence scoring
    
    Args:
        model: Trained hybrid model
        image_tensor: Input image (1, 3, H, W) or (3, H, W)
        device: Device to use
        class_names: Optional list of class names
        
    Returns:
        Prediction dict with confidence scores
    """
    model.eval()
    model = model.to(device)
    
    # Ensure batch dimension
    if image_tensor.dim() == 3:
        image_tensor = image_tensor.unsqueeze(0)
    
    image_tensor = image_tensor.to(device)
    
    with torch.no_grad():
        output = model(image_tensor)
    
    probs = output["probabilities"][0].cpu().numpy()
    confidence = output["confidence"][0].cpu().numpy()
    logits = output["logits"][0].cpu().numpy()
    
    top_k = 3
    top_indices = np.argsort(-probs)[:top_k]
    
    predictions = []
    for idx in top_indices:
        pred_dict = {
            "class_id": int(idx),
            "probability": float(probs[idx]),
            "confidence": float(confidence[idx]),
            "logit": float(logits[idx])
        }
        if class_names:
            pred_dict["class_name"] = class_names[idx]
        predictions.append(pred_dict)
    
    return {
        "top_predictions": predictions,
        "predicted_class": predictions[0].get("class_name", f"Class {predictions[0]['class_id']}"),
        "confidence_score": predictions[0]["confidence"],
        "attention_maps": output["attention_maps"]
    }
