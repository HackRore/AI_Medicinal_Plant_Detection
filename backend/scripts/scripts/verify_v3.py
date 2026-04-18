import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json
import os
from pathlib import Path

# Config
MODEL_DIR = Path(r"d:\PROJECT STAGE 1\ml_models")
MODEL_PATH = MODEL_DIR / "model_v3.pth"
CLASS_NAMES_PATH = MODEL_DIR / "class_names_v3.json"
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

def test_inference():
    if not MODEL_PATH.exists():
        print("Model v3 not found. Run scripts/train_v3.py first.")
        return

    with open(CLASS_NAMES_PATH, 'r') as f:
        class_names = json.load(f)

    model = load_v3_model(len(class_names))
    
    # Pick a random image from unified dataset
    UNIFIED_DIR = Path(r"d:\PROJECT STAGE 1\dataset\unified")
    first_species = os.listdir(UNIFIED_DIR)[0]
    sample_img_path = list((UNIFIED_DIR / first_species).glob("*"))[0]
    
    print(f"Testing with sample: {sample_img_path} ({first_species})")
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    img = Image.open(sample_img_path).convert('RGB')
    img_t = transform(img).unsqueeze(0).to(DEVICE)
    
    with torch.no_grad():
        outputs = model(img_t)
        _, predicted = torch.max(outputs, 1)
        confidence = torch.nn.functional.softmax(outputs, dim=1)[0][predicted].item()
        
    print(f"Prediction: {class_names[predicted.item()]} ({confidence*100:.2f}%)")
    print("Verification Successful! 🏅🎯🏁🏆⚖️🚩🏆🏁🏆")

if __name__ == "__main__":
    test_inference()
