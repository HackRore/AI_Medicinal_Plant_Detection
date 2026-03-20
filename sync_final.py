import os
import json

DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"
BACKEND_JSON = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"
PIPELINE_JSON = r"d:\PROJECT STAGE 1\ml_pipeline\models\class_names.json"

def sync_classes():
    if not os.path.exists(DATA_DIR):
        print("❌ Dataset not found.")
        return
        
    # Standard Keras flow_from_directory sorting
    classes = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    
    print(f"✅ Found {len(classes)} folders.")
    
    # Save to both locations
    for path in [BACKEND_JSON, PIPELINE_JSON]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(classes, f, indent=2)
        print(f"📦 Synchronized: {path}")

if __name__ == "__main__":
    sync_classes()
