"""
PLANTOAI LIVE BACKEND TEST
Tests the four required scenarios against the live Render backend.
"""
import requests
import urllib.request
import os
import io
from PIL import Image, ImageDraw
import json

BASE = "https://plantoai-backend.onrender.com"

def create_solid_image(color, size=(300, 300), filename="temp.jpg"):
    """Create a solid color test image."""
    img = Image.new("RGB", size, color=color)
    img.save(filename, "JPEG")
    return filename

def download_image(url, filename):
    """Download an image from a URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        with open(filename, "wb") as f:
            f.write(data)
        return filename
    except Exception as e:
        print(f"  Download failed: {e}")
        return None

def test_predict(image_path, label):
    """Send image to /api/v1/predict and report results."""
    print(f"\n{'='*55}")
    print(f"TEST: {label}")
    print(f"File: {image_path}")
    try:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
            resp = requests.post(f"{BASE}/api/v1/predict", files=files, timeout=60)
        
        print(f"HTTP Status: {resp.status_code}")
        data = resp.json()
        
        if data.get("success"):
            print(f"  ✅ IDENTIFIED: {data.get('class_name','?')}")
            print(f"  Confidence: {data.get('confidence_pct','?')}%  ({data.get('confidence_label','?')})")
            print(f"  Quality passed: {data.get('quality_passed')}")
        else:
            err = data.get("error", "Unknown")
            detail = data.get("details", "")
            gate = data.get("gate_rejection") or data.get("message") or ""
            if "not" in str(gate).lower() or "not" in str(err).lower():
                print(f"  ✅ CORRECTLY REJECTED: {gate or err}")
            else:
                print(f"  ⚠️  FAILED: {err} | {detail} | {gate}")
        return data
    except Exception as e:
        print(f"  ❌ EXCEPTION: {e}")
        return {}

print("="*55)
print("PLANTOAI LIVE BACKEND TEST — 4 SCENARIOS")
print(f"Backend: {BASE}")
print("="*55)

# --- TEST 0: Health check ---
print("\n[PRE-CHECK] Backend health...")
try:
    r = requests.get(f"{BASE}/api/v1/stats", timeout=15)
    d = r.json()
    print(f"  ✅ Backend LIVE — Species: {d.get('species_count')}, Accuracy: {d.get('top1_accuracy')}%")
except Exception as e:
    print(f"  ❌ Backend unreachable: {e}")
    exit(1)

# --- TEST 1: Real Leaf Photo (download from iNaturalist open API) ---
print("\n[TEST 1] Downloading real Tulsi leaf image...")
leaf_url = "https://inaturalist-open-data.s3.amazonaws.com/photos/1234567/medium.jpg"
# Fallback: use a small synthetic green image for now and flag it
leaf_path = download_image(
    "https://upload.wikimedia.org/wikipedia/commons/4/4e/Ocimum_tenuiflorum_-_Köhler–s_Medizinal-Pflanzen-115.jpg",
    "test_leaf.jpg"
)
if not leaf_path:
    # Create synthetic green leaf-colored image as fallback
    leaf_path = create_solid_image((34, 139, 34), filename="test_leaf.jpg")
    print("  Using synthetic green image (download blocked)")
test_predict("test_leaf.jpg", "TEST 1 — Leaf image (should identify a plant)")

# --- TEST 2: Non-leaf (hand / solid red) ---
print("\n[TEST 2] Creating non-leaf image (solid red - simulates hand/object)...")
create_solid_image((200, 60, 60), filename="test_hand.jpg")
test_predict("test_hand.jpg", "TEST 2 — Non-leaf (should be REJECTED)")

# --- TEST 3: Random non-plant (blue solid - simulates WhatsApp forward) ---
print("\n[TEST 3] Creating random non-plant image (blue/gray)...")
create_solid_image((70, 130, 180), filename="test_random.jpg")
test_predict("test_random.jpg", "TEST 3 — Random image (should be REJECTED)")

# --- TEST 4: Blurry/dark image ---
print("\n[TEST 4] Creating dark/blurry image...")
create_solid_image((15, 30, 15), size=(100, 100), filename="test_dark.jpg")
test_predict("test_dark.jpg", "TEST 4 — Dark/blurry (expect low confidence or rejection)")

# Cleanup
for f in ["test_leaf.jpg", "test_hand.jpg", "test_random.jpg", "test_dark.jpg"]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "="*55)
print("TEST COMPLETE")
print("="*55)
