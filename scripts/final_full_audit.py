import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader
import os
import json
from pathlib import Path
import time

# ── Configuration ──
UNIFIED_DIR = Path(r"d:\PROJECT STAGE 1\dataset\unified")
MODEL_PATH = Path(r"d:\PROJECT STAGE 1\ml_models\model_v3.pth")
CLASS_NAMES_PATH = Path(r"d:\PROJECT STAGE 1\ml_models\class_names_v3.json")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def run_full_audit():
    print("🚀 INITIATING GLOBAL BOTANICAL SYSTEM AUDIT")
    print("-" * 50)
    
    # 1. Load class names
    if not CLASS_NAMES_PATH.exists():
        print(f"Error: {CLASS_NAMES_PATH} not found.")
        return
    with open(CLASS_NAMES_PATH, 'r') as f:
        class_names = json.load(f)
    print(f"Auditing {len(class_names)} species: {class_names}")

    # 2. Reconstruct Model (ELU architecture)
    model = models.mobilenet_v2()
    n_inputs = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(n_inputs, 512),
        nn.ELU(),  # Standard for v3
        nn.Dropout(0.2),
        nn.Linear(512, len(class_names))
    )
    
    # 3. Load v3 Weights
    if not MODEL_PATH.exists():
        print(f"Error: {MODEL_PATH} not found.")
        return
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    print("Neural Backbone: ACTIVE (Triple-Intelligence v3)")

    # 4. Prepare Data for Audit
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    full_dataset = datasets.ImageFolder(str(UNIFIED_DIR), transform=transform)
    loader = DataLoader(full_dataset, batch_size=32, shuffle=False)
    
    print(f"Total Images for Rescan: {len(full_dataset)}")
    print("-" * 50)

    # 5. Execute Audit Scan
    correct = 0
    total = 0
    class_stats = {name: {"correct": 0, "total": 0} for name in class_names}
    
    start_time = time.time()
    
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # Per-class stats
            for i in range(len(labels)):
                target_idx = labels[i].item()
                pred_idx = predicted[i].item()
                target_name = class_names[target_idx]
                class_stats[target_name]["total"] += 1
                if target_idx == pred_idx:
                    class_stats[target_name]["correct"] += 1

    duration = time.time() - start_time
    final_acc = (correct / total) * 100

    # 6. Report Generation
    print("\n📊 AUDIT REPORT: IDENTIFIABILITY MATRIX")
    print("-" * 50)
    print(f"{'SPECIES':<15} | {'ACCURACY':<10} | {'TOTAL':<5}")
    print("-" * 50)
    for species, stats in class_stats.items():
        acc = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"{species:<15} | {acc:>8.2f}% | {stats['total']:>5}")
    
    print("-" * 50)
    print(f"GLOBAL AUDIT ACCURACY: {final_acc:.4f}%")
    print(f"TOTAL PROCESSING TIME: {duration:.2f}s")
    print(f"STATUS: {'🏆 SYSTEM PERFECT' if final_acc >= 99.9 else '⚠️ DRIFT DETECTED'}")
    print("-" * 50)

if __name__ == "__main__":
    run_full_audit()
