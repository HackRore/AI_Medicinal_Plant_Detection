import requests
import os
from PIL import Image

BASE = "https://plantoai-backend.onrender.com"

def create_image(color, size=(300,300), fname="tmp.jpg"):
    Image.new("RGB", size, color=color).save(fname, "JPEG")
    return fname

def raw_predict(path, label):
    print(f"\n--- {label} ---")
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/api/v1/predict", files={"file": (os.path.basename(path), f, "image/jpeg")}, timeout=60)
    print(f"Status: {r.status_code}")
    data = r.json()
    # Print ALL keys and values (truncated)
    for k, v in data.items():
        if k not in ("gradcam",):  # skip huge base64 blob
            val = str(v)[:120]
            print(f"  [{k}] = {val}")
    return data

# Test 1: Solid green (synthetic leaf color)
raw_predict(create_image((34,139,34), fname="t1.jpg"), "GREEN (leaf color)")

# Test 2: Solid red (non-leaf)
raw_predict(create_image((200,50,50), fname="t2.jpg"), "RED (non-leaf)")

# Test 3: Solid blue (random non-plant)
raw_predict(create_image((50,100,200), fname="t3.jpg"), "BLUE (non-plant)")

# Test 4: Near black (dark/unusable)
raw_predict(create_image((10,20,10), size=(100,100), fname="t4.jpg"), "DARK (bad quality)")

for f in ["t1.jpg","t2.jpg","t3.jpg","t4.jpg"]:
    if os.path.exists(f): os.remove(f)

print("\nDONE.")
