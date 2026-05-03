import os
import sys
import time
import requests
import multiprocessing
import uvicorn
import json
from PIL import Image
from io import BytesIO

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

def run_server():
    os.chdir("backend")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8005, log_level="error")

if __name__ == "__main__":
    print("--- FULL SYSTEM OOPS VALIDATION (LOCAL FORGE) ---")
    
    # 1. Start Backend in a separate process
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    
    # Give it time to load the 88-species model
    print("Waking up Neural Engine (88 species, 384px)...")
    time.sleep(20)
    
    base_url = "http://127.0.0.1:8005/api/v1/predict-url"
    
    try:
        # TEST 1: NEEM LEAF
        print("\n[TEST 1] IDENTIFYING: Azadirachta indica (Neem)")
        img_url = "https://inaturalist-open-data.s3.amazonaws.com/photos/169358846/medium.jpg"
        r = requests.post(base_url, data={'url': img_url}, timeout=30)
        res = r.json()
        
        if res.get('success'):
            print(f"✅ ID Success: {res['plant']['name']}")
            print(f"✅ Confidence: {res['prediction']['confidence']}%")
            print(f"✅ Reasoning: {res['reasoning']['analysis'][:100]}...")
            print(f"✅ Grad-CAM: {len(res['gradcam'].get('heatmap_url', '')) > 0}")
        else:
            print(f"❌ ID Failed: {res.get('error')}")

        # TEST 2: RED CAR (REJECTION)
        print("\n[TEST 2] REJECTING: Non-Botanical (Red Car)")
        car_url = "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&q=80&w=800"
        r = requests.post(base_url, data={'url': car_url}, timeout=30)
        res = r.json()
        
        if not res.get('success') and 'Not a Plant Leaf' in res.get('error', ''):
            print(f"✅ Rejection Success: {res['error']}")
            print(f"✅ AI Insight: {res['message']}")
        else:
            print(f"❌ Rejection Failed (Should have rejected car)")

    except Exception as e:
        print(f"ERROR DURING VALIDATION: {e}")
    finally:
        print("\nValidation Complete. Shutting down forge.")
        server_process.terminate()
        server_process.join()
