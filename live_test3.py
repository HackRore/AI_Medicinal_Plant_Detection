import requests, os, time
from PIL import Image

BASE = "https://plantoai-backend.onrender.com"

def create_image(color, size=(300,300), fname="tmp.jpg"):
    Image.new("RGB", size, color=color).save(fname, "JPEG")
    return fname

def predict_one(path, label, retries=2):
    print(f"\n--- {label} ---")
    for attempt in range(retries):
        try:
            with open(path, "rb") as f:
                r = requests.post(
                    f"{BASE}/api/v1/predict",
                    files={"file": (os.path.basename(path), f, "image/jpeg")},
                    timeout=90
                )
            data = r.json()
            for k,v in data.items():
                if k != "gradcam":
                    print(f"  {k}: {str(v)[:150]}")
            return data
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return {}

# Run tests with 8s gap between each to avoid rate limiting
t1 = create_image((34,139,34), fname="t1.jpg")
predict_one(t1, "TEST 1 - Green image (synthetic leaf)")
time.sleep(8)

t2 = create_image((200,50,50), fname="t2.jpg")
predict_one(t2, "TEST 2 - Red image (non-leaf)")
time.sleep(8)

t3 = create_image((50,100,200), fname="t3.jpg")
predict_one(t3, "TEST 3 - Blue image (non-plant)")
time.sleep(8)

t4 = create_image((10,20,10), size=(100,100), fname="t4.jpg")
predict_one(t4, "TEST 4 - Near-black (dark image)")

for f in ["t1.jpg","t2.jpg","t3.jpg","t4.jpg"]:
    if os.path.exists(f): os.remove(f)
print("\nALL TESTS DONE.")
