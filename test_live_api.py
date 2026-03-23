import os
import random
import requests
import json
import time

API_URL = "https://plantoai-backend.onrender.com/api/v1/predict/"
HEALTH_URL = "https://plantoai-backend.onrender.com/health"
DATASET_DIR = r"C:\Users\Dell\Downloads\HackRore\AI_Medicinal_Plant_Detection\dataset\merged_dataset"

print("="*60)
print("🌍 LIVE PRODUCTION API STRESS TEST")
print("="*60)

# Check Health First
try:
    print(f"Checking health: {HEALTH_URL}")
    r = requests.get(HEALTH_URL, timeout=30)
    print(f"Health Response: {r.json()}\n")
    if r.json().get('demo_mode') is True:
        print("⚠️ WARNING: API is still in DEMO MODE! The model might not be finished downloading or loaded.")
except Exception as e:
    print(f"Health check failed: {e}\n")

# Gather images
all_images = []
for root, dirs, files in os.walk(DATASET_DIR):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            all_images.append(os.path.join(root, f))

if not all_images:
    print("❌ No images found in dataset!")
    exit(1)

# Pick 3 random images
test_images = random.sample(all_images, min(3, len(all_images)))

for i, img_path in enumerate(test_images, 1):
    true_class = os.path.basename(os.path.dirname(img_path))
    print(f"🧪 Test #{i}")
    print(f"File: {os.path.basename(img_path)}")
    print(f"True Class: {true_class}")
    
    try:
        with open(img_path, 'rb') as f:
            start_time = time.time()
            response = requests.post(
                API_URL, 
                files={"file": (os.path.basename(img_path), f, "image/jpeg")},
                timeout=60
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Prediction: {data.get('predicted_class')}")
                print(f"📊 Confidence: {(data.get('confidence', 0)*100):.1f}%")
                print(f"⏱️ Speed: {elapsed:.2f} seconds")
                print(f"🏷️ Demo Mode: {data.get('demo_mode')}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Request Failed: {e}")
    print("-" * 60)
