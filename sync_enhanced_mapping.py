import json
import os

ENHANCED_JSON = r"d:\PROJECT STAGE 1\ml_pipeline\models\enhanced\class_names.json"
BACKEND_JSON = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"

def sync_enhanced_classes():
    if not os.path.exists(ENHANCED_JSON):
        print(f"❌ Enhanced JSON not found: {ENHANCED_JSON}")
        return
        
    with open(ENHANCED_JSON, 'r') as f:
        mapping_dict = json.load(f)
        
    # Standardize: Sort keys by their index value
    sorted_classes = [None] * 80
    for name, idx in mapping_dict.items():
        if idx < 80:
            sorted_classes[idx] = name
            
    # Check for gaps
    if None in sorted_classes:
        print("⚠️ Warning: Gaps found in class mapping!")
        
    with open(BACKEND_JSON, 'w') as f:
        json.dump(sorted_classes, f, indent=2)
    print(f"✅ Synchronized 80 classes to {BACKEND_JSON}")

if __name__ == "__main__":
    sync_enhanced_classes()
