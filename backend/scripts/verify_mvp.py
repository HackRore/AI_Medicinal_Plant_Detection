import requests, sys, os

# Try to find a port that's listening — default 8000
BASE = "http://localhost:8000"
ERRORS = []

def check(name, condition, detail=""):
    if condition:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name} {detail}")
        ERRORS.append(name)

def run_tests():
    print("── Health check ──")
    try:
        r = requests.get(f"{BASE}/health").json()
        check("Backend online", r.get("status") == "ok")
        check("Model loaded",   r.get("model_loaded") == True)
        check("Classes == 12",    r.get("classes", 0) == 12, f"(got {r.get('classes')})")
    except Exception as e:
        print(f"  ✗ Could not connect to backend: {e}")
        return

    print("── Plants list ──")
    try:
        r = requests.get(f"{BASE}/api/v1/plants").json()
        check("Plants returned",      len(r.get("plants", [])) > 0)
        check("Has toxicity field",   "toxicity" in r["plants"][0] if r.get("plants") else False)
        check("Has ayurvedic_uses",   "ayurvedic_uses" in r["plants"][0] if r.get("plants") else False)
    except Exception as e:
        print(f"  ✗ Plants list check failed: {e}")

    print("── Prediction test ──")
    # Find any image in dataset to test with
    test_img = None
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "unified_dataset")
    for root, dirs, files in os.walk(dataset_path):
        for f in files:
            if f.lower().endswith(('.jpg','.jpeg','.png')):
                test_img = os.path.join(root, f)
                break
        if test_img: break

    if test_img:
        print(f"    Testing with image: {os.path.basename(test_img)}")
        with open(test_img, "rb") as f:
            try:
                r = requests.post(f"{BASE}/api/v1/predict", files={"file": f}).json()
                if "success" not in r:
                    # Try alternate path
                    r = requests.post(f"{BASE}/predict", files={"file": f}).json()
                
                check("Prediction response success",     r.get("success") == True)
                if r.get("success"):
                    check("Has confidence",         r.get("prediction", {}).get("confidence") is not None)
                    check("Has toxicity",           r.get("toxicity") is not None)
                    check("Has ayurvedic_uses",     len(r.get("medicinal", {}).get("ayurvedic_uses", [])) > 0)
                    check("Has gradcam overlay",    bool(r.get("gradcam", {}).get("overlay_base64")))
                    conf = r.get("prediction", {}).get("confidence", 0)
                    print(f"    Predicted: {r.get('plant',{}).get('scientific_name')} | Confidence: {conf}%")
            except Exception as e:
                print(f"  ✗ Prediction request failed: {e}")
    else:
        print(f"  ! No test image found in {dataset_path}")

    print("── OOD rejection test ──")
    try:
        import numpy as np
        from PIL import Image
        from io import BytesIO
        noise = Image.fromarray(np.random.randint(0,255,(100,100,3),dtype=np.uint8))
        buf = BytesIO(); noise.save(buf, format="JPEG"); buf.seek(0)
        r = requests.post(f"{BASE}/api/v1/predict", files={"file": ("noise.jpg", buf, "image/jpeg")}).json()
        check("OOD rejected (low confidence image)", r.get("success") == False or r.get("prediction",{}).get("confidence",100) < 40)
    except Exception as e:
        print(f"  ✗ OOD test failed (pip install numpy pillow may be needed): {e}")

    print(f"\n{'ALL CHECKS PASSED ✓' if not ERRORS else f'FAILED: {ERRORS}'}")

if __name__ == "__main__":
    run_tests()
