import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import timm
import os
import json
import time
import sys

# --- CONFIGURATION ---
DATA_DIR = "dataset/FINAL_MONOLITH"
MODEL_NAME = "tf_efficientnetv2_s.in21k"
BATCH_SIZE = 16 # Reduced for CPU stability
EPOCHS = 30
LEARNING_RATE = 0.001
IMG_SIZE = 224
SAVE_PATH = "backend/ml_models/plantoai_v2.onnx"

def train_forge():
    print(f"🚀 Initializing Neural Forge v2.0 Monolith...")
    sys.stdout.flush()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device: {device}")

    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandAugment(num_ops=2, magnitude=9),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    if not os.path.exists(DATA_DIR):
        print(f"  ERROR: Data directory {DATA_DIR} not found.")
        return

    dataset = datasets.ImageFolder(DATA_DIR, transform=transform)
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = torch.utils.data.random_split(dataset, [train_size, val_size])

    # Windows Stability: num_workers=0
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    class_names = dataset.classes
    num_classes = len(class_names)
    print(f"  Classes Found: {num_classes}")
    print(f"  Total Images: {len(dataset)}")

    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open("backend/ml_models/class_names_v2.json", "w") as f:
        json.dump(class_names, f)

    print(f"  Loading {MODEL_NAME}...")
    model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.OneCycleLR(optimizer, max_lr=LEARNING_RATE, 
                                            steps_per_epoch=len(train_loader), epochs=EPOCHS)

    print(f"🔥 Forge Started. Target: 30 Epochs.")
    sys.stdout.flush()
    
    best_acc = 0.0
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        start_time = time.time()
        
        batch_idx = 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            scheduler.step()
            running_loss += loss.item()
            
            if batch_idx % 50 == 0:
                print(f"    Epoch {epoch+1} | Batch {batch_idx}/{len(train_loader)} | Loss: {loss.item():.4f}", end='\r')
                sys.stdout.flush()
            batch_idx += 1

        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        acc = 100 * correct / total
        print(f"\n  ✅ Epoch {epoch+1} Summary | Loss: {running_loss/len(train_loader):.4f} | Acc: {acc:.2f}% | Time: {time.time()-start_time:.1f}s")
        sys.stdout.flush()

        if acc > best_acc:
            best_acc = acc
            print(f"  ✨ Best Accuracy! Exporting ONNX...")
            dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(device)
            torch.onnx.export(model, dummy_input, SAVE_PATH, 
                            input_names=['input'], output_names=['output'],
                            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})

if __name__ == "__main__":
    train_forge()
