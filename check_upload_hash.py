import requests
import os
import hashlib

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def check_hash():
    # Use Aloevera sample
    folder_path = os.path.join(DATA_DIR, "Aloevera")
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        print("❌ No images found")
        return

    img_path = os.path.join(folder_path, images[0])
    
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
        
    local_hash = hashlib.md5(img_bytes).hexdigest()
    print(f"📤 CLIENT SENDING HASH: {local_hash}")
    
    files = {'file': (images[0], img_bytes, 'image/jpeg')}
    try:
        response = requests.post(API_URL, files=files)
        print(f"📡 API Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Response: {response.json().get('predicted_plant')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_hash()
