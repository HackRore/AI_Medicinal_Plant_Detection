import requests
import json

def test_live_backend():
    print("--- LIVE BACKEND REAL-TIME VALIDATION ---")
    url = "https://plantoai-backend.onrender.com/api/v1/predict-url"
    
    # 1. Test Neem Leaf
    print("\nTesting Case 1: Neem Leaf (Real URL)...")
    payload = {
        'url': 'https://inaturalist-open-data.s3.amazonaws.com/photos/169358846/medium.jpg',
        'scale_reference': 'false'
    }
    try:
        r = requests.post(url, data=payload, timeout=60)
        print(f"Status Code: {r.status_code}")
        data = r.json()
        print(f"Result: {data.get('plant', {}).get('name')} ({data.get('prediction', {}).get('confidence')}%)")
        print(f"Reasoning: {data.get('reasoning', {}).get('analysis')}")
        
        if data.get('success'):
            print("[SUCCESS] CASE 1")
    except Exception as e:
        print(f"[FAILED] CASE 1: {e}")

    # 2. Test Non-Leaf (Red Car)
    print("\nTesting Case 2: Red Car (Non-Leaf)...")
    payload = {
        'url': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&q=80&w=800',
        'scale_reference': 'false'
    }
    try:
        r = requests.post(url, data=payload, timeout=60)
        print(f"Status Code: {r.status_code}")
        data = r.json()
        print(f"Success: {data.get('success')}")
        print(f"Error Message: {data.get('error')}")
        print(f"Insight: {data.get('message')}")
        
        if not data.get('success') and 'Not a Plant Leaf' in data.get('error', ''):
            print("[SUCCESS] CASE 2 (Correctly Rejected)")
    except Exception as e:
        print(f"[FAILED] CASE 2: {e}")

if __name__ == "__main__":
    test_live_backend()
