import requests
import os
import json

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def empirical_relabel():
    folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    print(f"🕵️‍♂️ Reconstructing Mapping for {len(folders)} species...")
    
    mapping = {} # index -> folder_name
    
    for folder in folders:
        path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:1]
        if not images: continue
        
        img_path = os.path.join(path, images[0])
        with open(img_path, 'rb') as f:
            files = {'file': (images[0], f, 'image/jpeg')}
            try:
                # Use a special header or just parse the result
                # Since I added logging to MLService, I can also check logs.
                # But here I'll try to get the index from the 'predicted_class_index' if it exists.
                response = requests.post(API_URL, files=files, timeout=30)
                if response.status_code == 200:
                    res = response.json()
                    idx = res.get("predicted_class_index")
                    if idx is not None:
                        mapping[idx] = folder
                        print(f"📁 {folder:25} -> Index {idx}")
                    else:
                         print(f"⚠️ No index in response for {folder}: {res}")
                else:
                    print(f"❌ API Error for {folder}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Error processing {folder}: {e}")
                continue

    # Create the final list
    final_list = ["Unknown / Non-Medicinal"] * 80
    for idx, name in mapping.items():
        if idx < 80:
            final_list[idx] = name
            
    with open("empirical_class_names.json", "w") as f:
        json.dump(final_list, f, indent=2)
    print("✅ Empirical Mapping Saved!")

if __name__ == "__main__":
    empirical_relabel()
