import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import json

# ── Configuration ──
MODEL_PATH = r'd:\PROJECT STAGE 1\ml_models\model_v3.pth'
CLASS_NAMES_PATH = r'd:\PROJECT STAGE 1\ml_models\class_names_v3.json'
TEST_IMAGE = r'd:\PROJECT STAGE 1\dataset\unified\Banana\20210218_154608.jpg'

def debug_prediction():
    # 1. Load class names
    with open(CLASS_NAMES_PATH, 'r') as f:
        class_names = json.load(f)
    print(f"DEBUG: Loaded classes {class_names}")

    # 2. Build model (MUST USE ELU)
    model = models.mobilenet_v2()
    n_inputs = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(n_inputs, 512),
        nn.ELU(),  # <--- CRITICAL FIX
        nn.Dropout(0.2),
        nn.Linear(512, len(class_names))
    )
    
    # 3. Load weights
    model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
    model.eval()
    print("DEBUG: Model weights loaded successfully.")

    # 4. Preprocess
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 5. Predict
    img = Image.open(TEST_IMAGE).convert('RGB')
    inputs = preprocess(img).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(inputs)
        probs = torch.nn.functional.softmax(outputs, dim=1)[0]
        confidence, best_idx = torch.max(probs, 0)
    
    predicted_label = class_names[best_idx]
    print(f"\n🚀 DEBUG RESULT")
    print(f"Target Species: Banana")
    print(f"Predicted: {predicted_label}")
    print(f"Confidence: {confidence.item()*100:.2f}%")
    
    if predicted_label == "Banana":
        print("\n✅ ACCURACY VERIFIED: ELU Fix confirmed! 🏅")
    else:
        print("\n❌ STILL WRONG: Check class mapping or training weights.")

if __name__ == "__main__":
    debug_prediction()
