import sys
import os
import numpy as np
from PIL import Image
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock settings/env to avoid DB issues during standalone test
os.environ["MOBILENET_MODEL_PATH"] = "./ml_models/mobilenetv2_best.onnx"
os.environ["DATABASE_URL"] = "sqlite:///./medicinal_plants.db"

from backend.app.services.ml_service import MLService

def standalone_proof():
    print("🧠 Starting Standalone AI Proof (Direct MLService Access)...")
    ml = MLService()
    ml.load_models()
    
    DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"
    test_folders = ["Aloevera", "Neem", "Tulsi", "Turmeric"]
    
    # Load class names for mapping
    with open(r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json", 'r') as f:
        class_names = json.load(f)
    
    for folder in test_folders:
        path = os.path.join(DATA_DIR, folder)
        if not os.path.exists(path):
            continue
            
        images = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        img_path = os.path.join(path, images[0])
        
        with open(img_path, 'rb') as f:
            image_bytes = f.read()
            
        result = ml.predict(image_bytes)
        pred = result["predicted_class"]
        conf = result["confidence"]
        
        status = "✅ PASS" if pred.lower().replace(" ", "") in folder.lower().replace(" ", "") or folder.lower() in pred.lower() else "❌ FAIL"
        print(f"{status} | Actual: {folder:10} | Predicted: {pred} ({conf*100:.1f}%)")

if __name__ == "__main__":
    standalone_proof()
