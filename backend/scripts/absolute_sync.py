import json
import os

ENHANCED_JSON = r"d:\PROJECT STAGE 1\ml_pipeline\models\enhanced\class_names.json"
BACKEND_JSON = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"

def absolute_sync():
    with open(ENHANCED_JSON, 'r') as f:
        mapping_dict = json.load(f)
    
    # Create list of 80 names
    # Mapping dict is {"Name": Index}
    final_list = [""] * 80
    for name, idx in mapping_dict.items():
        if idx < 80:
            final_list[idx] = name
            
    with open(BACKEND_JSON, 'w') as f:
        json.dump(final_list, f, indent=2)
    print(f"✅ Absolute Sync Complete: {len(final_list)} classes in {BACKEND_JSON}")

if __name__ == "__main__":
    absolute_sync()
