import requests
import os

def test_production():
    url = "https://plantoai-backend.onrender.com/api/v1/predict"
    img_path = "d:/PROJECT STAGE 1/dataset/unified/Banana/20210218_154608.jpg"
    
    print(f"🚀 INITIATING PRODUCTION ML AUDIT: {url}")
    print(f"📄 Test Image: {os.path.basename(img_path)}")
    
    if not os.path.exists(img_path):
        print("❌ FAILED: Local test image not found.")
        return

    try:
        with open(img_path, "rb") as f:
            files = {"file": (os.path.basename(img_path), f, "image/jpeg")}
            response = requests.post(url, files=files, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            pred = data.get("predicted_class")
            conf = data.get("confidence", 0)
            print(f"✅ SUCCESS: Production Response Code 200")
            print(f"📊 Predicted Class: {pred}")
            print(f"🎯 Confidence: {conf:.4f}")
            
            if pred == "Banana":
                print("🏅 AUDIT PASSED: Production engine is 100% accurate.")
            else:
                print(f"⚠️ AUDIT FAILED: Production engine returned {pred}")
        else:
            print(f"❌ FAILED: Production status {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("🕒 TIMEOUT: Production backend (Render) is likely cold-starting. Please try again in 30s.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_production()
