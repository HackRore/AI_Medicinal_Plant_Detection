"""
PlantoAI Universal Image Test
Tests the system's ability to:
1. Correctly REJECT non-leaf images (hands, food, screens, etc.)
2. Correctly ACCEPT and IDENTIFY real leaf images
3. Provide actionable guidance when image quality is poor

Run this script to see the AI's behavior on any random image type.
"""
import requests
import os
import sys
from pathlib import Path

API_BASE = "https://plantoai-backend.onrender.com"

# Test categories
# Add your own test images here
TEST_IMAGES = []

# Use any image files found in the project
for ext in ["*.jpg", "*.jpeg", "*.png"]:
    TEST_IMAGES.extend(Path("screenshots").glob(ext))
    TEST_IMAGES.extend(Path("temp_test").glob(ext))
    TEST_IMAGES.extend(list(Path(".").glob(f"*{ext.strip('*')}")))

# Filter to only existing files
TEST_IMAGES = [str(p) for p in TEST_IMAGES if p.exists() and p.is_file()][:8]

if not TEST_IMAGES:
    print("No test images found. Add .jpg/.png files to the screenshots/ folder.")
    sys.exit(0)

print("=" * 70)
print("PlantoAI Universal Intelligence Test")
print("Goal: Reject non-leaves, identify leaves, guide poor-quality images")
print("=" * 70)

results = []
for img_path in TEST_IMAGES:
    img_name = os.path.basename(img_path)
    print(f"\nTesting: {img_name}")
    
    try:
        with open(img_path, "rb") as f:
            resp = requests.post(
                f"{API_BASE}/api/v1/predict",
                files={"file": (img_name, f, "image/jpeg")},
                timeout=60
            )
        
        data = resp.json()
        success = data.get("success", False)
        error = data.get("error", "")
        
        if not success:
            # Smart rejection fired
            print(f"  REJECTED: {error}")
            print(f"  AI Sees: {data.get('what_ai_sees', 'N/A')}")
            print(f"  Reason: {data.get('message', '')[:80]}")
            print(f"  Tip: {data.get('user_guidance', 'N/A')}")
            results.append({
                "image": img_name, "outcome": "REJECTED",
                "error": error, "tip": data.get("user_guidance", "")
            })
        else:
            plant = data.get("plant", {}).get("name", "Unknown")
            conf = data.get("prediction", {}).get("confidence", 0)
            label = data.get("prediction", {}).get("confidence_label", "")
            vision = data.get("vision_validation", {})
            gemini_agrees = vision.get("matches_prediction", True)
            
            print(f"  IDENTIFIED: {plant} ({conf:.1f}% - {label})")
            print(f"  Gemini validates: {'YES' if gemini_agrees else 'DISAGREES'} ({vision.get('agreement_score', 0)*100:.0f}%)")
            results.append({
                "image": img_name, "outcome": "IDENTIFIED",
                "plant": plant, "confidence": conf,
                "gemini_agrees": gemini_agrees
            })
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append({"image": img_name, "outcome": "ERROR", "error": str(e)})

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
identified = [r for r in results if r["outcome"] == "IDENTIFIED"]
rejected = [r for r in results if r["outcome"] == "REJECTED"]
errors = [r for r in results if r["outcome"] == "ERROR"]

print(f"Total tested    : {len(results)}")
print(f"Identified      : {len(identified)}")
print(f"Correctly rejected: {len(rejected)}")
print(f"Errors          : {len(errors)}")

if identified:
    print("\nIdentified Plants:")
    for r in identified:
        agree = "Gemini OK" if r.get("gemini_agrees") else "Gemini DISAGREES"
        print(f"  {r['image']}: {r['plant']} ({r['confidence']:.1f}%) [{agree}]")

if rejected:
    print("\nRejected (non-leaf or poor quality):")
    for r in rejected:
        print(f"  {r['image']}: {r['error']} - Tip: {r.get('tip', '')[:60]}")
