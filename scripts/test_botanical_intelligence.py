import os
import random
import json
import time
from io import BytesIO
from PIL import Image
import numpy as np
import onnxruntime as ort

# Add parent directory to path so we can import app
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.ml_service import MLService

def test_model():
    print("=== PlantoAI Neural Intelligence Test ===")
    
    # Initialize service
    service = MLService()
    if not service.model_loaded:
        print("FAIL: Model failed to load. Check paths.")
        return

    # Define test mapping (Folder Name -> Expected Class Name in model)
    test_classes = {
        "Mango": "Mango",
        "Neem": "Neem",
        "Guava": "Guava"
    }

    dataset_root = "dataset/unified"
    results = []

    for folder_name, expected_name in test_classes.items():
        folder_path = os.path.join(dataset_root, folder_name)
        if not os.path.exists(folder_path):
            print(f"⚠️ Folder not found: {folder_path}")
            continue

        print(f"\nTesting Class: {folder_name} (Expected: {expected_name})")
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not images:
            print("  No images found.")
            continue

        sample_size = min(5, len(images))
        sample = random.sample(images, sample_size)

        class_correct = 0
        for img_name in sample:
            img_path = os.path.join(folder_path, img_name)
            
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            
            prediction = service.predict(img_bytes)
            
            if prediction["success"]:
                predicted = prediction["predicted_class"]
                conf = prediction["confidence_pct"]
                is_correct = (predicted.lower() == expected_name.lower())
                if is_correct:
                    class_correct += 1
                
                status = "[OK]" if is_correct else "[FAIL]"
                print(f"  {status} {img_name}: Predicted={predicted} ({conf}%)")
            else:
                print(f"  ❌ {img_name}: Error={prediction.get('error')}")

        results.append({
            "class": folder_name,
            "accuracy": (class_correct / sample_size) * 100,
            "correct": class_correct,
            "total": sample_size
        })

    print("\n=== TEST SUMMARY ===")
    overall_correct = sum(r["correct"] for r in results)
    overall_total = sum(r["total"] for r in results)
    
    for r in results:
        print(f"{r['class']}: {r['accuracy']:.1f}% ({r['correct']}/{r['total']})")
    
    if overall_total > 0:
        print(f"\nOVERALL ACCURACY: {(overall_correct/overall_total)*100:.1f}%")
    else:
        print("\nNo tests performed.")

if __name__ == "__main__":
    test_model()
