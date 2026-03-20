import requests
import os
import json

API_URL = "http://127.0.0.1:8000/api/v1/predict/"
DATASET_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def test_prediction():
    # Pick a random leaf from dataset
    classes = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
    if not classes:
        print("❌ Dataset not found at path.")
        return
    
    test_class = classes[0]
    class_path = os.path.join(DATASET_DIR, test_class)
    images = [f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        print(f"❌ No images in {test_class}")
        return
    
    img_path = os.path.join(class_path, images[0])
    print(f"🔍 Testing with image: {img_path}")
    
    with open(img_path, 'rb') as f:
        files = {'file': (images[0], f, 'image/jpeg')}
        try:
            response = requests.post(API_URL, files=files)
            print(f"📡 Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("✅ Result:")
                print(json.dumps(result, indent=2))
                
                if result.get("plant_details") is None:
                    print("\n🚨 CRITICAL: plant_details is NULL")
                    if result.get("storage_status") == "filtered_out":
                        print("👉 Reason: STORAGE FILTER (Confidence too low or Gap too small)")
                    else:
                        print("👉 Reason: DB Lookup failed (Species name mismatch)")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_prediction()
