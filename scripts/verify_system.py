import sys
import os
import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"
API_V1 = f"{BASE_URL}/api/v1"

# Test Image Path (Use one found in dataset)
TEST_IMAGE_PATH = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset\Parijatha\IMG_20190919_075315826.jpg"

def log(message):
    print(message)
    try:
        with open("verification_results.log", "a", encoding="utf-8") as f:
            f.write(str(message) + "\n")
    except:
        pass

def print_status(message, status):
    symbol = "[OK]" if status else "[FAIL]"
    log(f"{symbol} {message}")

def verify_health():
    log("\n--- 1. Testing Health Endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_status(f"Backend Healthy: {response.json()}", True)
            return True
        else:
            print_status(f"Backend Unhealthy: {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Backend Connection Failed: {e}", False)
        return False

def verify_prediction():
    log("\n--- 2. Testing Prediction Endpoint (MobileNetV2 + ViT) ---")
    if not os.path.exists(TEST_IMAGE_PATH):
        print_status(f"Test image not found at {TEST_IMAGE_PATH}", False)
        return False
    
    try:
        files = {'file': ('test_leaf.jpg', open(TEST_IMAGE_PATH, 'rb'), 'image/jpeg')}
        start = time.time()
        response = requests.post(f"{API_V1}/predict/", files=files)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"Prediction Success in {duration:.2f}s", True)
            log(f"   Predicted Plant: {data.get('predicted_plant')}")
            log(f"   Confidence: {data.get('confidence')}")
            log(f"   Model Version: {data.get('model_version')}")
            return True
        else:
            print_status(f"Prediction Failed: {response.text}", False)
            return False
    except Exception as e:
        print_status(f"Prediction Error: {e}", False)
        return False

def verify_gemini_integration():
    log("\n--- 3. Testing Gemini Integration via Backend ---")
    # We will try the describe endpoint with dummy data since we might not wait for image upload persistence
    # Actually, let's use the Chat endpoint which is easier to test without a prior prediction ID if we mock it, 
    # but the API requires a valid plant_id.
    
    # Alternative: check if /predict returned plant details (which it should)
    pass

def verify_frontend():
    log("\n--- 4. Testing Frontend Availability ---")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print_status("Frontend Accessible", True)
            return True
        else:
            print_status(f"Frontend returned {response.status_code}", False)
            return False
    except Exception as e:
        print_status(f"Frontend Connection Failed: {e}", False)
        return False

def main():
    # Clear log file
    with open("verification_results.log", "w", encoding="utf-8") as f:
        f.write("--- VERIFICATION LOG ---\n")

    log("STARTING COMPLETION SYSTEM VERIFICATION")
    
    backend_ok = verify_health()
    if backend_ok:
        verify_prediction()
    
    verify_frontend()
    
    log("\nVerification Sequence Complete")

if __name__ == "__main__":
    main()
