import requests
import os
import json
import time

API_URL = "http://127.0.0.1:8000/api/v1/predict"
TEST_IMAGES = {
    "Banana": r"d:\PROJECT STAGE 1\dataset\unified\Banana\20210218_154608.jpg",
    "Mango": r"d:\PROJECT STAGE 1\dataset\unified\Mango\20210222_155901.jpg",
    "Neem": r"d:\PROJECT STAGE 1\dataset\unified\Neem\20210220_142211.jpg"
}

def session_deep_audit():
    print("🔬 INITIATING MULTI-SPECIES SYSTEM DEEP AUDIT")
    print("-" * 50)
    
    for species, path in TEST_IMAGES.items():
        if not os.path.exists(path):
            print(f"⚠️ Skipping {species}: File not found.")
            continue
            
        print(f"Testing Identification: {species}...", end="", flush=True)
        try:
            with open(path, "rb") as f:
                files = {"file": (os.path.basename(path), f, "image/jpeg")}
                response = requests.post(API_URL, files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # Unified response format check
                pred = data.get("predicted_class") or data.get("plant_name")
                conf = data.get("confidence", 0)
                # Ensure confidence is 0-100 for display
                conf_display = conf if conf > 1 else conf * 100
                
                db_sync = "YES" if data.get("plant_details") and data["plant_details"].get("id") != 0 else "NO (Resilient Fallback)"
                
                print(f" DONE")
                print(f"  Result: {pred}")
                print(f"  Confidence: {conf_display:.2f}%")
                print(f"  DB Data Synced: {db_sync}")
                
                if pred.lower() == species.lower():
                    print(f"  ✅ {species} IDENTIFICATION PERFECT!")
                else:
                    print(f"  ❌ {species} MISIDENTIFIED AS {pred}")
            else:
                print(f" ERROR: {response.status_code}")
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f" FAILED: {e}")
        print("-" * 50)

if __name__ == "__main__":
    session_deep_audit()
