import requests
import os
import json

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATASET_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def cross_check():
    test_folders = ["Aloevera", "Amla", "Neem", "Tulsi", "Turmeric"]
    
    for folder in test_folders:
        path = os.path.join(DATASET_DIR, folder)
        if not os.path.exists(path):
            print(f"⚠️ Folder {folder} not found.")
            continue
            
        images = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            print(f"⚠️ No images in {folder}")
            continue
            
        img_path = os.path.join(path, images[0])
        with open(img_path, 'rb') as f:
            files = {'file': (images[0], f, 'image/jpeg')}
            response = requests.post(API_URL, files=files)
            if response.status_code == 200:
                result = response.json()
                pred = result.get("predicted_plant")
                conf = result.get("confidence")
                print(f"📁 Actual: {folder} | 🤖 Predicted: {pred} ({conf*100:.1f}%)")
            else:
                print(f"❌ Error testing {folder}")

if __name__ == "__main__":
    cross_check()
