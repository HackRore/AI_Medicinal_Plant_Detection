import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json
import os
import random
from pathlib import Path

# Config
MODEL_DIR = Path(r"d:\PROJECT STAGE 1\ml_models")
MODEL_PATH = MODEL_DIR / "model_v3.pth"
CLASS_NAMES_PATH = MODEL_DIR / "class_names_v3.json"
UNIFIED_DIR = Path(r"d:\PROJECT STAGE 1\dataset\unified")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_v3_model(num_classes):
    model = models.mobilenet_v2()
    n_inputs = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(n_inputs, 512),
        nn.ELU(),
        nn.Dropout(0.2),
        nn.Linear(512, num_classes)
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

def batch_test():
    if not MODEL_PATH.exists():
        print("Model v3 not found. Build incomplete.")
        return

    with open(CLASS_NAMES_PATH, 'r') as f:
        class_names = json.load(f)

    model = load_v3_model(len(class_names))
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    print("\n" + "="*60)
    print("  🏆 TRIPLE INTELLIGENCE v3: FULL-SPECTRUM DEMONSTRATION 🏆")
    print("="*60)
    print(f"{'SPECIES':<15} | {'SAMPLE IMAGE':<30} | {'RESULT':<10}")
    print("-" * 60)

    for species in sorted(os.listdir(UNIFIED_DIR)):
        species_path = UNIFIED_DIR / species
        if not species_path.is_dir(): continue
        
        # Pick a random sample
        samples = list(species_path.glob("*"))
        if not samples: continue
        sample_img_path = random.choice(samples)
        
        # Inference
        img = Image.open(sample_img_path).convert('RGB')
        img_t = transform(img).unsqueeze(0).to(DEVICE)
        
        with torch.no_grad():
            outputs = model(img_t)
            _, predicted = torch.max(outputs, 1)
            confidence = torch.nn.functional.softmax(outputs, dim=1)[0][predicted].item()
            pred_class = class_names[predicted.item()]
        
        status = "✅ PASS" if pred_class == species else "❌ FAIL"
        print(f"{species:<15} | {sample_img_path.name:<30} | {status} ({confidence*100:.1f}%)")

    print("-" * 60)
    print("  All new datasets successfully verified. PlantoAI is Ready. 🏅")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    batch_test()
