import requests
import os
import json

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"
OUTPUT_FILE = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"

def empirical_build():
    mapping = {} # idx -> name
    folders = [f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))]
    
    # Pre-fill with "Unknown" for all 80 slots (MobileNet is usually 80)
    for i in range(80):
        mapping[i] = "Unknown"

    print(f"🔍 Querying API for {len(folders)} folders...")
    
    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images: continue
        
        img_path = os.path.join(folder_path, images[0])
        with open(img_path, 'rb') as f:
            files = {'file': (images[0], f.read(), 'image/jpeg')}
            try:
                # Use a small timeout to keep things moving
                response = requests.post(API_URL, files=files, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    idx = data.get('predicted_class_index')
                    conf = data.get('confidence')
                    if idx is not None:
                        if idx == -1:
                            print(f"⚠️ {folder} -> BELOW THRESHOLD (Conf: {conf:.4f})")
                        elif mapping[idx] == "Unknown":
                            mapping[idx] = folder
                            print(f"✅ {folder} -> Index {idx} (Conf: {conf:.4f})")
            except Exception as e:
                print(f"❌ Error for {folder}: {e}")

    # Convert to list [0..79]
    class_list = [mapping[i] for i in range(80)]
    
    # Save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(class_list, f, indent=2)
    print(f"🎉 Successfully wrote {OUTPUT_FILE}")

if __name__ == "__main__":
    empirical_build()
