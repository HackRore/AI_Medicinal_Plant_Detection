import requests
import os
import json

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def diagnose():
    print("🧪 Running Dataset Accuracy Diagnosis...")
    test_species = ["Aloevera", "Neem", "Tulsi", "Turmeric", "Lemon", "Mango"]
    
    results = []
    
    for species in test_species:
        folder_path = os.path.join(DATA_DIR, species)
        if not os.path.exists(folder_path):
            print(f"⚠️ Folder not found: {species}")
            continue
            
        # Get first image
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            continue
            
        img_path = os.path.join(folder_path, images[0])
        
        with open(img_path, 'rb') as f:
            files = {'file': (images[0], f, 'image/jpeg')}
            try:
                response = requests.post(API_URL, files=files)
                if response.status_code == 200:
                    res = response.json()
                    pred = res.get("predicted_plant")
                    conf = res.get("confidence")
                    idx = res.get("predicted_class_index")
                    
                    status = "✅" if species.lower() in pred.lower() or pred.lower() in species.lower() else "❌"
                    print(f"{status} {species:10} -> Predicted: {pred:15} (Idx: {idx}, Conf: {conf:.2f})")
                    results.append({"actual": species, "predicted": pred, "index": idx, "status": status})
                else:
                    print(f"❌ API Error for {species}: {response.text}")
            except Exception as e:
                print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    diagnose()
