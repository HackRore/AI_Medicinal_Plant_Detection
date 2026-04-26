import requests
import time

BASE = "https://plantoai-backend.onrender.com"
IMG_PATH = r"D:\PROJECT FINAL\dataset\IMLD\test\images\0000_jpg.rf.7bf8d4c69ad253ee55c87d6e78d1ae28.jpg"

print("=" * 60)
print("LIVE PREDICT TEST — Local dataset image")
print("=" * 60)

with open(IMG_PATH, "rb") as f:
    img_bytes = f.read()
print(f"Image loaded: {len(img_bytes)} bytes")

print("Sending to /api/v1/predict on Render...")
start = time.time()
r = requests.post(
    f"{BASE}/api/v1/predict",
    files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
    timeout=60
)
elapsed = round((time.time() - start) * 1000)

print(f"HTTP Status: {r.status_code} ({elapsed}ms)")
d = r.json()

success = d.get("success", False)
conf_raw = d.get("confidence", 0)
conf = conf_raw * 100 if conf_raw < 1 else d.get("confidence_pct", conf_raw)
plant = d.get("class_name") or d.get("predicted_class") or "Unknown"
top3 = d.get("top3", [])
err = d.get("error") or d.get("details")

print(f"Success: {success}")
print(f"Identified as: {plant}")
print(f"Confidence: {round(conf, 2)}%")

if top3:
    print("Top 3:")
    for t in top3:
        name = t.get("name", "?")
        tc = round(t.get("confidence", 0) * 100, 1)
        print(f"  - {name}: {tc}%")

if err:
    print(f"Error field: {err}")

print()
if conf < 2.5 and success:
    print("VERDICT: NORMALIZATION FIX NOT LIVE YET on Render (confidence too low)")
    print("ACTION NEEDED: Redeploy Render backend with latest commit")
elif conf >= 5 and success:
    print("VERDICT: NORMALIZATION FIX IS ACTIVE - system working correctly")
elif not success:
    print("VERDICT: Prediction failed — check error above")

print()
print("Raw response snippet:")
print(str(d)[:400])
