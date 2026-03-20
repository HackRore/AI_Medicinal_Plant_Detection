import requests
import os
import hashlib

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
IMG_PATH = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset\Aloevera\2.jpg"

def test_determinism():
    if not os.path.exists(IMG_PATH):
        print("❌ Image not found")
        return

    with open(IMG_PATH, 'rb') as f:
        img_bytes = f.read()
    
    print(f"🧪 Testing determinism for {os.path.basename(IMG_PATH)}...")
    indices = []
    for i in range(5):
        files = {'file': (os.path.basename(IMG_PATH), img_bytes, 'image/jpeg')}
        try:
            response = requests.post(API_URL, files=files)
            if response.status_code == 200:
                idx = response.json().get('predicted_class_index')
                indices.append(idx)
                print(f"Iteration {i+1}: Index {idx}")
            else:
                print(f"Iteration {i+1}: ERROR {response.status_code}")
        except Exception as e:
            print(f"Iteration {i+1}: Connection Error: {e}")

    if len(set(indices)) == 1:
        print("✅ DETERMINISTIC: All iterations returned the same index.")
    else:
        print("❌ NON-DETERMINISTIC: Indices vary!")

if __name__ == "__main__":
    test_determinism()
