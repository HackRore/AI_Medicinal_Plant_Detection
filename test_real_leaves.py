import requests, os, time

BASE = "https://plantoai-backend.onrender.com"
headers = {"User-Agent": "PlantoAI-Test/1.0"}

# Check stats
r = requests.get(f"{BASE}/api/v1/stats", timeout=15)
print("Stats:", r.json().get("species_count"), "species,", r.json().get("top1_accuracy"), "% accuracy")

# Real leaf images from iNaturalist S3 (open access)
urls = [
    ("neem_leaf.jpg",   "https://inaturalist-open-data.s3.amazonaws.com/photos/169358846/medium.jpg"),
    ("tulsi_leaf.jpg",  "https://inaturalist-open-data.s3.amazonaws.com/photos/102921891/medium.jpg"),
    ("aloe_leaf.jpg",   "https://inaturalist-open-data.s3.amazonaws.com/photos/22067958/medium.jpg"),
]

for fname, url in urls:
    try:
        img = requests.get(url, headers=headers, timeout=15)
        if img.status_code != 200:
            print(f"{fname}: download failed {img.status_code}")
            continue
        with open(fname, "wb") as f:
            f.write(img.content)
        print(f"\nTesting {fname} ({len(img.content)//1024}KB)...")

        with open(fname, "rb") as f:
            pred = requests.post(f"{BASE}/api/v1/predict",
                files={"file": (fname, f, "image/jpeg")}, timeout=90)
        d = pred.json()
        if d.get("success"):
            name = d.get("plant", {}).get("name", "?")
            conf = d.get("prediction", {}).get("confidence", 0)
            label = d.get("prediction", {}).get("confidence_label", "?")
            print(f"  IDENTIFIED: {name} | Confidence: {conf}% [{label}]")
        else:
            print(f"  REJECTED: {d.get('error')} | conf={d.get('confidence', '?')}%")
            print(f"  Message: {d.get('message', '')}")
        os.remove(fname)
        time.sleep(6)
    except Exception as e:
        print(f"  Exception: {e}")

print("\nDONE.")
