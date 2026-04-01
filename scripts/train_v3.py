import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os
from pathlib import Path
import json

# Config
UNIFIED_DIR = Path(r"d:\PROJECT STAGE 1\dataset\unified")
MODEL_DIR = Path(r"d:\PROJECT STAGE 1\ml_models")
MODEL_PATH = MODEL_DIR / "model_v3.pth"
CLASS_NAMES_PATH = MODEL_DIR / "class_names_v3.json"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_model(num_classes):
    model = models.mobilenet_v2(weights='DEFAULT')
    n_inputs = model.classifier[1].in_features
    # Custom head with ELU for faster convergence
    model.classifier[1] = nn.Sequential(
        nn.Linear(n_inputs, 512),
        nn.ELU(),
        nn.Dropout(0.2),
        nn.Linear(512, num_classes)
    )
    return model.to(DEVICE)

def train_efficiently():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = datasets.ImageFolder(str(UNIFIED_DIR), transform=transform)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    class_names = dataset.classes
    with open(CLASS_NAMES_PATH, 'w') as f:
        json.dump(class_names, f)
        
    model = build_model(len(class_names))
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Training on {len(class_names)} classes with {len(dataset)} images...")
    
    # Fast 3-epoch training for efficiency
    for epoch in range(3):
        model.train()
        running_loss = 0.0
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            
        print(f"Epoch {epoch+1}/3 - Loss: {running_loss/len(dataloader):.4f}")
    
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    
    # Export to ONNX (for TFLite conversion)
    print("Exporting to ONNX...")
    dummy_input = torch.randn(1, 3, 224, 224).to(DEVICE)
    onnx_path = MODEL_DIR / "model_v3.onnx"
    torch.onnx.export(model, dummy_input, str(onnx_path), input_names=['input'], output_names=['output'])
    
    # Note: TFLite conversion usually happens via onnx2tf or similar tools
    # For this POC, we will use the .pth model in our verification script.
    print(f"ONNX export complete at {onnx_path}")

if __name__ == "__main__":
    if UNIFIED_DIR.exists():
        train_efficiently()
    else:
        print("Unified dataset not found. Please run scripts/unified_refinery.py first.")
