"""
Training Script
Trains a MobileNetV2 model on selected medicinal plants and exports to ONNX.
"""

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"
OUTPUT_DIR = r"d:\PROJECT STAGE 1\backend\ml_models"
MODEL_PATH = os.path.join(OUTPUT_DIR, "mobilenetv2_full.onnx")
CLASS_NAMES_PATH = os.path.join(OUTPUT_DIR, "class_names_full.json")

def train():
    logger.info("Starting FULL DATASET training pipeline...")
    
    # 0. Check Data
    if not os.path.exists(DATA_DIR):
        logger.error(f"Dataset not found at {DATA_DIR}")
        return

    # 1. Setup Data Transformations
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])

    # 2. Train/Val Split + Balancing
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.utils.class_weight import compute_class_weight
        import numpy as np

        full_dataset = datasets.ImageFolder(DATA_DIR, transform=data_transforms)
        logger.info(f"Full dataset: {len(full_dataset.classes)} classes, {len(full_dataset)} images")
        
        # Split 80/20 stratified
        targets = [s[1] for s in full_dataset.samples]
        train_idx, val_idx = train_test_split(range(len(targets)), test_size=0.2, stratify=targets, random_state=42)
        
        train_sampler = torch.utils.data.Subset(full_dataset, train_idx)
        val_sampler = torch.utils.data.Subset(full_dataset, val_idx)
        
        train_loader = torch.utils.data.DataLoader(train_sampler, batch_size=32, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_sampler, batch_size=32, shuffle=False)
        
        # Class weights
        class_counts = np.bincount(targets)
        class_weights = 1. / class_counts
        class_weights = class_weights / class_weights.sum()
        class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
        
        logger.info(f"Train/Val split: {len(train_idx)}/{len(val_idx)} images")
        
    except Exception as e:
        logger.error(f"Error splitting dataset: {e}")
        return

    # 3. Setup Model (MobileNetV2)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    logger.info(f"Training on {device}")
    
    model = models.mobilenet_v2(pretrained=True)
    
    # Freeze feature layers
    for param in model.parameters():
        param.requires_grad = False
        
    # Replace Classifier
    model.classifier[1] = nn.Linear(model.last_channel, len(wanted_classes))
    model.to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=2)

    # Early stopping
    best_val_loss = float('inf')
    patience_counter = 0

    epochs = 10
    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        # Val
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        train_acc = train_correct / train_total
        val_acc = val_correct / val_total
        logger.info(f"Epoch {epoch+1}: Train Loss {train_loss/len(train_loader):.4f} Acc {train_acc:.4f} | Val Loss {val_loss/len(val_loader):.4f} Acc {val_acc:.4f}")
        
        scheduler.step(val_loss / len(val_loader))
        
        # Early stop
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), os.path.join(OUTPUT_DIR, 'best_model.pth'))
        else:
            patience_counter += 1
            if patience_counter >= 5:
                logger.info("Early stopping")
                break

    # Load best model for export
    model.load_state_dict(torch.load(os.path.join(OUTPUT_DIR, 'best_model.pth')))
    
    # 5. Export to ONNX
    logger.info("Exporting best model to ONNX...")
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    torch.onnx.export(model, dummy_input, MODEL_PATH, 
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
    
    logger.info(f"Model saved to {MODEL_PATH}")

    # 6. Save Class Names (full common names)
    final_class_names = full_dataset.classes
    with open(CLASS_NAMES_PATH, 'w') as f:
        json.dump(final_class_names, f)
        
    logger.info(f"Class names saved: {len(final_class_names)} classes")
    logger.info("Training Complete!")

if __name__ == "__main__":
    train()
