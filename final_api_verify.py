import requests
import os
import json

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATASET_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def final_verify():
    test_folders = ["Aloevera", "Neem", "Tulsi", "Turmeric"]
    print("🚀 Starting Final API Verification...")
    
    for folder in test_folders:
        path = os.path.join(DATASET_DIR, folder)
        if not os.path.exists(path):
            continue
            
        images = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            continue
            
        img_path = os.path.join(path, images[0])
        with open(img_path, 'rb') as f:
            files = {'file': (images[0], f, 'image/jpeg')}
            try:
                response = requests.post(API_URL, files=files)
                if response.status_code == 200:
                    result = response.json()
                    pred = result.get("predicted_plant")
                    conf = result.get("confidence")
                    status = "✅ PASS" if pred.lower().replace(" ", "") in folder.lower().replace(" ", "") or folder.lower() in pred.lower() else "❌ FAIL"
                    print(f"{status} | Actual: {folder:10} | Predicted: {pred} ({conf*100:.1f}%)")
                else:
                    print(f"❌ API Error for {folder}: {response.text}")
            except Exception as e:
                print(f"❌ Connection Error for {folder}: {e}")

if __name__ == "__main__":
    final_verify()
