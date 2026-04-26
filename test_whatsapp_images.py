import requests
import time
import os

BASE = "https://plantoai-backend.onrender.com"
IMAGE_DIR = r"C:\Users\HackRore\OneDrive\Desktop\Temp testing Leaf Images"

images = [
    "WhatsApp Image 2026-04-27 at 00.09.18.jpeg",
    "WhatsApp Image 2026-04-27 at 00.09.43.jpeg",
    "WhatsApp Image 2026-04-27 at 00.09.8.jpeg",
    "WhatsApp Image 2026-04-27 at 00.10.37.jpeg"
]

print("=" * 60)
print("LIVE STRESS TEST — USER'S WHATSAPP IMAGES")
print("=" * 60)

results = []

for img_name in images:
    path = os.path.join(IMAGE_DIR, img_name)
    if not os.path.exists(path):
        print(f"File missing: {img_name}")
        continue
        
    print(f"\nProcessing: {img_name}")
    with open(path, "rb") as f:
        img_bytes = f.read()
    
    start = time.time()
    try:
        r = requests.post(
            f"{BASE}/api/v1/predict",
            files={"file": (img_name, img_bytes, "image/jpeg")},
            timeout=60
        )
        elapsed = round((time.time() - start) * 1000)
        
        if r.status_code != 200:
            print(f"  FAIL: HTTP {r.status_code}")
            continue
            
        d = r.json()
        success = d.get("success", False)
        plant = d.get("plant", {}).get("name", "Unknown")
        conf = d.get("prediction", {}).get("confidence", 0)
        label = d.get("prediction", {}).get("confidence_label", "Low")
        
        print(f"  Result: {plant} ({round(conf, 1)}%) — [{label}]")
        print(f"  Time: {elapsed}ms")
        
        results.append({
            "image": img_name,
            "plant": plant,
            "confidence": conf,
            "label": label,
            "success": success
        })
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("FINAL SUMMARY FOR README")
print("=" * 60)
for res in results:
    icon = "✅" if res["confidence"] >= 12 else "⚠️"
    print(f"| {res['image']} | {res['plant']} | {round(res['confidence'],1)}% | {res['label']} | {icon} |")
