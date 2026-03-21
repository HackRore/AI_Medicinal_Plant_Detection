"""
Hybrid Model Training Script
Train EfficientNet + Swin Transformer model on medicinal plant dataset
"""

import os
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping

from PIL import Image
from tqdm import tqdm

# Import models
from ml_pipeline.models.efficientnet_swin import EfficientNetSwinHybrid, HybridModelTrainer
from ml_pipeline.models.quality_gatekeeper import QualityGatekeeper

logger = logging.getLogger(__name__)


class MedicinalPlantDataset(Dataset):
    """Dataset for medicinal plant leaf images"""
    
    def __init__(
        self,
        data_dir: Path,
        split: str = 'train',
        transform=None,
        quality_check: bool = True
    ):
        """
        Args:
            data_dir: Path to training data root
            split: 'train', 'val', or 'test'
            transform: Image transformations
            quality_check: Apply quality filtering
        """
        self.data_dir = Path(data_dir)
        self.split = split
        self.transform = transform or self._get_default_transforms()
        self.quality_check = quality_check
        self.gatekeeper = QualityGatekeeper() if quality_check else None
        
        # Scan directory for class folders
        self.classes = sorted([
            d.name for d in self.data_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ])
        self.class2idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        # Collect all images
        self.images = []
        self._collect_images()
    
    def _collect_images(self):
        """Collect and filter images by quality"""
        for class_name in self.classes:
            class_dir = self.data_dir / class_name
            image_files = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
            
            for img_path in image_files:
                # Optional quality check
                if self.quality_check:
                    try:
                        with open(img_path, 'rb') as f:
                            result = self.gatekeeper.check_quality(f.read())
                        if not result['is_valid']:
                            logger.debug(f"Skipping low-quality image: {img_path}")
                            continue
                    except Exception as e:
                        logger.warning(f"Error checking quality of {img_path}: {e}")
                        continue
                
                self.images.append((img_path, self.class2idx[class_name]))
        
        logger.info(f"Found {len(self.images)} valid images across {len(self.classes)} classes")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path, label = self.images[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            logger.error(f"Error loading {img_path}: {e}")
            # Return random valid image
            rand_idx = np.random.randint(0, len(self))
            return self.__getitem__(rand_idx)
    
    def _get_default_transforms(self):
        """Default image augmentation pipeline"""
        if self.split == 'train':
            return transforms.Compose([
                transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 0.5)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        else:
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])


class HybridModelLightning(pl.LightningModule):
    """PyTorch Lightning wrapper for hybrid model training"""
    
    def __init__(
        self,
        num_classes: int,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
    ):
        super().__init__()
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        
        self.model = EfficientNetSwinHybrid(num_classes=num_classes)
        self.criterion = nn.CrossEntropyLoss()
    
    def forward(self, x):
        return self.model(x)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        output = self(x)
        logits = output['logits']
        
        loss = self.criterion(logits, y)
        
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        self.log('train_loss', loss, prog_bar=True)
        self.log('train_acc', acc, prog_bar=True)
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        output = self(x)
        logits = output['logits']
        
        loss = self.criterion(logits, y)
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_acc', acc, prog_bar=True)
    
    def test_step(self, batch, batch_idx):
        x, y = batch
        output = self(x)
        logits = output['logits']
        
        loss = self.criterion(logits, y)
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        self.log('test_loss', loss)
        self.log('test_acc', acc)
    
    def configure_optimizers(self):
        optimizer = AdamW(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )
        scheduler = CosineAnnealingLR(optimizer, T_max=100)
        
        return {
            'optimizer': optimizer,
            'lr_scheduler': {
                'scheduler': scheduler,
                'interval': 'epoch'
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description='Train hybrid EfficientNet + Swin Transformer model'
    )
    parser.add_argument('--data-dir', type=str, required=True,
                        help='Path to training data root')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=1e-3,
                        help='Learning rate')
    parser.add_argument('--output-dir', type=str, default='./models',
                        help='Output directory for checkpoints')
    parser.add_argument('--device', type=str, default='auto',
                        help='Device: cuda, cpu, or auto')
    parser.add_argument('--quality-check', action='store_true',
                        help='Apply quality filtering')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')
    
    args = parser.parse_args()
    
    # Setup
    torch.manual_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Loading data from {args.data_dir}")
    
    # Load dataset
    full_dataset = MedicinalPlantDataset(
        args.data_dir,
        split='train',
        quality_check=args.quality_check
    )
    
    num_classes = len(full_dataset.classes)
    logger.info(f"Found {num_classes} plant classes")
    logger.info(f"Total images: {len(full_dataset)}")
    
    # Split data
    train_size = int(0.7 * len(full_dataset))
    val_size = int(0.15 * len(full_dataset))
    test_size = len(full_dataset) - train_size - val_size
    
    train_data, val_data, test_data = random_split(
        full_dataset, [train_size, val_size, test_size]
    )
    
    # Create dataloaders
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=args.batch_size)
    test_loader = DataLoader(test_data, batch_size=args.batch_size)
    
    # Model and trainer
    model = HybridModelLightning(
        num_classes=num_classes,
        learning_rate=args.learning_rate
    )
    
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath=output_dir,
        filename='best-{epoch}-{val_acc:.3f}',
        monitor='val_acc',
        mode='max',
        save_top_k=3,
        verbose=True
    )
    
    early_stop = EarlyStopping(
        monitor='val_acc',
        patience=15,
        mode='max',
        verbose=True
    )
    
    # Trainer
    trainer = pl.Trainer(
        max_epochs=args.epochs,
        callbacks=[checkpoint_callback, early_stop],
        accelerator='auto',
        devices='auto' if args.device == 'auto' else [args.device],
        log_every_n_steps=10,
        enable_progress_bar=True
    )
    
    # Train
    logger.info("Starting training...")
    trainer.fit(
        model,
        train_dataloaders=train_loader,
        val_dataloaders=val_loader
    )
    
    # Test
    logger.info("Running tests...")
    trainer.test(model, dataloaders=test_loader, ckpt_path='best')
    
    # Save class names
    class_names_file = output_dir / 'class_names.json'
    with open(class_names_file, 'w') as f:
        json.dump(full_dataset.classes, f, indent=2)
    
    logger.info(f"Training complete! Model saved to {output_dir}")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
