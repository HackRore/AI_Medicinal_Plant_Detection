import requests
import json
import os
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_symptom_search():
    print("\n[TEST] Symptom Search (RAG/Local)...")
    url = f"{BASE_URL}/symptom-search"
    payload = {"symptoms": "I have a severe cough and persistent fever"}
    try:
        r = requests.post(url, json=payload, timeout=30)
        data = r.json()
        print(f"Status: {r.status_code}")
        print(f"Source: {data.get('source')}")
        if data.get("recommendations"):
            print(f"Recommendations Found: {len(data['recommendations'])}")
            print(f"Sample: {data['recommendations'][0]['plant']}")
        
        # Valid sources now include Local Mode
        if data.get("source") and ("Neural RAG" in data["source"] or "Clinical Engine" in data["source"]):
            print("V Verification: SUCCESS")
        else:
            print("X Verification: FAILED (Source mismatch)")
    except Exception as e:
        print(f"X Error: {e}")

def test_prediction():
    print("\n[TEST] Prediction (BioCLIP Gate)...")
    url = f"{BASE_URL}/predict"
    sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "public", "samples", "neem.jpg")
    sample_path = os.path.normpath(sample_path)
    
    try:
        with open(sample_path, "rb") as f:
            files = {"file": ("neem.jpg", f, "image/jpeg")}
            r = requests.post(url, files=files, timeout=60)
            data = r.json()
            print(f"Status: {r.status_code}")
            if data.get("success"):
                print(f"V Prediction: SUCCESS ({data['plant']['name']})")
                print(f"Confidence: {data['prediction']['confidence']}%")
            else:
                print(f"X Prediction: {data.get('status', 'ERROR')} - {data.get('message', data.get('error'))}")
                if 'botanical_confidence' in data:
                    print(f"Gate Score: {data['botanical_confidence']}%")
    except Exception as e:
        print(f"X Error: {e}")

if __name__ == "__main__":
    test_symptom_search()
    test_prediction()
