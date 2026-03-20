import requests
import os
import json

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"
OUTPUT_FILE = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"

def robust_empirical_build():
    # mapping: idx -> (folder_name, confidence)
    best_mapping = {}
    
    folders = [f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))]
    print(f"🔍 Analyzing {len(folders)} species folders for 80-Class Master Model...")

    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images: continue
        
        # Test up to 3 images to find the most consistent index
        found_indices = []
        for i in range(min(3, len(images))):
            img_path = os.path.join(folder_path, images[i])
            with open(img_path, 'rb') as f:
                files = {'file': (images[i], f.read(), 'image/jpeg')}
                try:
                    response = requests.post(API_URL, files=files, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        idx = data.get('predicted_class_index')
                        conf = data.get('confidence')
                        if idx is not None and idx != -1:
                            found_indices.append((idx, conf))
                except Exception as e:
                    print(f"❌ Error for {folder} [{i}]: {e}")

        if found_indices:
            # Pick the index with HIGHEST confidence across the tested images
            idx, conf = max(found_indices, key=lambda x: x[1])
            
            if idx not in best_mapping or conf > best_mapping[idx][1]:
                if idx in best_mapping:
                    old_folder, old_conf = best_mapping[idx]
                    print(f"🔄 Index {idx}: Replaced {old_folder} ({old_conf:.4f}) with {folder} ({conf:.4f})")
                else:
                    print(f"✅ Index {idx}: Found {folder} ({conf:.4f})")
                best_mapping[idx] = (folder, conf)

    # Convert to list [0..79]
    class_list = ["Unknown"] * 80
    for idx, (folder, conf) in best_mapping.items():
        if 0 <= idx < 80:
            class_list[idx] = folder
    
    # Final check for "Unknown" to See if we missed anything
    missing = [i for i, name in enumerate(class_list) if name == "Unknown"]
    print(f"📊 Mapping Complete. Missing indices: {len(missing)}")

    # Save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(class_list, f, indent=2)
    print(f"🎉 Successfully wrote {OUTPUT_FILE}")

if __name__ == "__main__":
    robust_empirical_build()
