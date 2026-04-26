"""
PREDICT TEST — Downloads a leaf image and tests the /predict endpoint directly.
"""
import requests
import time
import io

BASE = "https://plantoai-backend.onrender.com"

def download_image(url, label):
    r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code == 200 and len(r.content) > 1000:
        print(f"  Downloaded {label}: {len(r.content)} bytes OK")
        return r.content
    print(f"  Failed to download {label}: HTTP {r.status_code}")
    return None

# Try multiple real leaf images
test_images = [
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Holy_Basil_%28Ocimum_tenuiflorum%29.JPG/320px-Holy_Basil_%28Ocimum_tenuiflorum%29.JPG", "Tulsi/Holy Basil"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Neem_A_Vogel.jpg/320px-Neem_A_Vogel.jpg", "Neem"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Simple_AloeVera.jpg/320px-Simple_AloeVera.jpg", "Aloe Vera"),
]

print("=" * 60)
print("LIVE PREDICT ENDPOINT TEST WITH REAL LEAF IMAGES")
print("=" * 60)

for url, label in test_images:
    print(f"\nTesting with: {label}")
    img_bytes = download_image(url, label)
    if not img_bytes:
        continue
    
    start = time.time()
    try:
        files = {"file": (f"{label.replace('/', '_')}.jpg", img_bytes, "image/jpeg")}
        r = requests.post(f"{BASE}/api/v1/predict", files=files, timeout=60)
        elapsed = round((time.time() - start) * 1000)
        
        if r.status_code != 200:
            print(f"  FAIL: HTTP {r.status_code} — {r.text[:200]}")
            continue
            
        d = r.json()
        success = d.get("success", False)
        
        # Handle both confidence formats
        conf_raw = d.get("confidence", 0)
        confidence = conf_raw * 100 if conf_raw < 1 else d.get("confidence_pct", conf_raw)
        
        plant = d.get("class_name") or d.get("predicted_class") or "Unknown"
        top3 = d.get("top3", [])
        error = d.get("error") or d.get("details", "")
        
        print(f"  Status: HTTP {r.status_code} ({elapsed}ms)")
        print(f"  Success: {success}")
        print(f"  Identified as: {plant}")
        print(f"  Confidence: {round(confidence, 1)}%")
        if top3:
            top3_str = ", ".join([f"{t.get('name','?')} ({round(t.get('confidence',0)*100,1)}%)" for t in top3])
            print(f"  Top 3: {top3_str}")
        if error:
            print(f"  Error: {error}")
        
        # Normalization check: if confidence suspiciously low on everything, old code
        if confidence < 2.5 and success:
            print("  WARN: Confidence is very low — normalization fix may NOT be active on Render yet")
        elif confidence >= 5:
            print("  OK: Confidence looks healthy — normalization fix appears active")
            
    except Exception as e:
        print(f"  EXCEPTION: {e}")
    
    # Only need one successful test
    break

print("\n" + "=" * 60)
print("RAW RESPONSE (first 500 chars):")
print("=" * 60)
try:
    print(r.text[:500])
except:
    pass
