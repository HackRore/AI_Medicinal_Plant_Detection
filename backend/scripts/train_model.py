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
MODEL_PATH = os.path.join(OUTPUT_DIR, "mobilenetv2_best.onnx")
CLASS_NAMES_PATH = os.path.join(OUTPUT_DIR, "class_names.json")

# Mapping: Folder Name -> Scientific Name (DB Key)
CLASS_MAPPING = {
    "Tulsi": "Ocimum_tenuiflorum",
    "Neem": "Azadirachta_indica",
    "Aloevera": "Aloe_vera",
    "Mint": "Mentha",
    "Amruthaballi": "Tinospora_cordifolia"
}

def train():
    logger.info("Starting training pipeline...")
    
    # 0. Check Data
    if not os.path.exists(DATA_DIR):
        logger.error(f"Dataset not found at {DATA_DIR}")
        return

    # 1. Setup Data Transformations
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]) # MobileNetV2 usually expects [-1, 1] or similar normalization
    ])

    # 2. Filter Dataset
    # We only want the 5 classes we support in the DB
    try:
        full_dataset = datasets.ImageFolder(DATA_DIR, transform=data_transforms)
        
        # Get indices of the classes we want
        wanted_classes = list(CLASS_MAPPING.keys())
        wanted_indices = [i for i, c in enumerate(full_dataset.classes) if c in wanted_classes]
        
        # Create a mapping from stats.classes index to our new 0-4 index
        # And ensure the order matches the scientific names mapping
        
        # Actually, simpler: create a custom dataset or subset
        # But for 'ImageFolder', it assumes all folders are classes. 
        # We will create a list of samples (path, class_index) for ONLY our classes.
        
        samples = []
        class_to_idx = {cls: i for i, cls in enumerate(wanted_classes)} # 0: Tulsi, 1: Neem...
        
        for path, target in full_dataset.samples:
            folder_name = full_dataset.classes[target]
            if folder_name in wanted_classes:
                samples.append((path, class_to_idx[folder_name]))
                
        if len(samples) == 0:
            logger.error("No images found for the target classes!")
            return

        # Hack ImageFolder to only have our samples
        full_dataset.samples = samples
        full_dataset.classes = wanted_classes
        full_dataset.class_to_idx = class_to_idx
        
        logger.info(f"Found {len(samples)} images for {len(wanted_classes)} classes.")

        dataloader = torch.utils.data.DataLoader(full_dataset, batch_size=32, shuffle=True)
        
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
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
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)

    # 4. Train (Quick Fine-tuning)
    epochs = 3 # Keep it small for this demo/setup task
    model.train()
    
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss/len(dataloader):.4f} - Acc: {correct/total:.4f}")

    # 5. Export to ONNX
    logger.info("Exporting to ONNX...")
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    torch.onnx.export(model, dummy_input, MODEL_PATH, 
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
    
    logger.info(f"Model saved to {MODEL_PATH}")

    # 6. Save Class Names (Mapped to Scientific Names)
    # The model predicts index 0..4. Index 0 corresponds to wanted_classes[0] ('Tulsi').
    # We map 'Tulsi' -> 'Ocimum_tenuiflorum' using global mapping.
    
    final_class_names = [CLASS_MAPPING[cls] for cls in wanted_classes]
    
    with open(CLASS_NAMES_PATH, 'w') as f:
        json.dump(final_class_names, f)
        
    logger.info(f"Class names saved to {CLASS_NAMES_PATH}: {final_class_names}")
    logger.info("Training Complete!")

if __name__ == "__main__":
    train()
