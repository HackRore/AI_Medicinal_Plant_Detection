import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import os
import json
import time

# SETTINGS AS PER G9 SPEC
BATCH_SIZE = 32
EPOCHS = 10  # Production hardening
LEARNING_RATE = 0.001
DATASET_PATH = "dataset/unified_dataset"
MODEL_SAVE_PATH = "backend/app/model/efficientnetv2_medicinal.pth"
ONNX_SAVE_PATH = "backend/app/model/efficientnetv2_medicinal.onnx"

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    dataset = datasets.ImageFolder(DATASET_PATH, transform=transform)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    # SAVE CLASS NAMES FOR BACKEND SYNC
    os.makedirs("backend/app/model", exist_ok=True)
    with open("backend/app/model/class_index.json", "w") as f:
        json.dump(dataset.classes, f)

    # MODEL: EfficientNetV2-S (The G9 Scientific Standard)
    model = models.efficientnet_v2_s(weights='IMAGENET1K_V1')
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(dataset.classes))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print(f"Starting training on {len(dataset.classes)} species...")
    model.train()
    for epoch in range(EPOCHS):
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(loader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            if i % 10 == 0:
                print(f"Epoch {epoch+1}, Batch {i}, Loss: {loss.item():.4f}")
        
    print("TRAINING COMPLETE. SAVING MODEL...")
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    
    # EXPORT TO ONNX FOR PRODUCTION (Render/Vercel parity)
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    torch.onnx.export(model, dummy_input, ONNX_SAVE_PATH, 
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
    print(f"ONNX MODEL SAVED: {ONNX_SAVE_PATH}")

if __name__ == "__main__":
    train()
