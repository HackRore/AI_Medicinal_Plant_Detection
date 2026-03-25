import requests
import json
import os

BASE_URL = "https://plantoai-backend.onrender.com/api/v1"
TEST_IMAGE = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset\Turmeric\g.1.jpg"

def test_plants():
    print("\n--- Testing Plants (Database Fallback) ---")
    try:
        res = requests.get(f"{BASE_URL}/plants/")
        print(f"Status: {res.status_code}")
        data = res.json()
        print(f"Total: {data.get('total')}")
        print(f"Source: {data.get('source')}")
        print(f"First plant: {data.get('plants', [{}])[0].get('name') or data.get('plants', [{}])[0].get('species_name')}")
    except Exception as e:
        print(f"Error: {e}")

def test_symptoms():
    print("\n--- Testing Symptom Search ---")
    try:
        payload = {"symptoms": "fever and cough"}
        res = requests.post(f"{BASE_URL}/symptom-search", json=payload)
        print(f"Status: {res.status_code}")
        data = res.json()
        if "recommendations" in data:
            print(f"Found {len(data['recommendations'])} recommendations.")
            print(f"Top plant: {data['recommendations'][0]['plant']}")
        else:
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")

def test_predict():
    print("\n--- Testing Neural Scanner (Model) ---")
    try:
        if not os.path.exists(TEST_IMAGE):
            print(f"Test image not found at {TEST_IMAGE}")
            return
        
        with open(TEST_IMAGE, "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            res = requests.post(f"{BASE_URL}/predict/", files=files)
            print(f"Status: {res.status_code}")
            data = res.json()
            print(f"Predicted: {data.get('predicted_class')}")
            print(f"Confidence: {data.get('confidence')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_plants()
    test_symptoms()
    test_predict()
