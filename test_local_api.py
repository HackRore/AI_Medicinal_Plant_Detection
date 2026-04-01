import requests
import json
import time
import os

def test_local_prediction():
    image_path = r"d:\PROJECT STAGE 1\dataset\unified\Banana\20210218_154608.jpg"
    if not os.path.exists(image_path):
        print(f"Sample not found at {image_path}")
        return

    url = "http://127.0.0.1:8000/api/v1/predict"
    
    print("\n🚀 TESTING LIVELY LOCAL API (PREDICTION)")
    print("-" * 40)
    
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: SUCCESS ✅")
        print(f"Species Identified: {data.get('predicted_class')}")
        print(f"Confidence: {data.get('confidence')*100:.2f}%")
        print(f"Model Engine: {data.get('model_version')}")
        print("-" * 40)
        return True
    else:
        print(f"Prediction Failed ❌: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    test_local_prediction()
