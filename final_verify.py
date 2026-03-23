import requests
import time
print("PLANTOAI FINAL VERIFICATION")
print("="*50)

# 1. GitHub release exists
r = requests.get(
    "https://api.github.com/repos/HackRore/AI_Medicinal_Plant_Detection/releases/tags/v1.0",
    timeout=30
)
if r.status_code == 200:
    data = r.json()
    assets = data.get('assets', [])
    model_asset = next((a for a in assets if 'h5' in a['name']), None)
    print(f"GitHub Release v1.0 : EXISTS")
    print(f"Model file attached : {'YES - ' + str(model_asset['size']//1024//1024) + 'MB' if model_asset else 'NO - UPLOAD NEEDED'}")
else:
    print(f"GitHub Release v1.0 : MISSING - {r.status_code}")
    print("ACTION: Go to github.com/HackRore/AI_Medicinal_Plant_Detection/releases/new")

# 2. Backend health
print()
try:
    r = requests.get(
        "https://plantoai-backend.onrender.com/api/v1/health",
        timeout=60
    )
    data = r.json()
    print(f"Backend status  : {r.status_code}")
    print(f"Model loaded    : {data.get('model_loaded', 'N/A')}")
    print(f"Demo mode       : {data.get('demo_mode', 'N/A')}")
    print(f"Classes         : {data.get('num_classes', 'N/A')}")
except Exception as e:
    print(f"Backend         : OFFLINE - {e}")

# 3. Test real prediction
print()
import os
DATASET = r'C:\Users\Dell\Downloads\HackRore\AI_Medicinal_Plant_Detection\dataset\merged_dataset'
test_img = None
folder_name = None
if os.path.exists(DATASET):
    for root, dirs, files in os.walk(DATASET):
        for f in files:
            if f.lower().endswith('.jpg'):
                test_img = os.path.join(root, f)
                folder_name = os.path.basename(root)
                break
        if test_img:
            break

if test_img:
    print(f"Testing with    : {folder_name}")
    try:
        with open(test_img, 'rb') as f:
            r = requests.post(
                "https://plantoai-backend.onrender.com/api/v1/predict",
                files={"file": (os.path.basename(test_img), f, "image/jpeg")},
                timeout=120
            )
        result = r.json()
        print(f"Plant detected  : {result.get('predicted_class', result.get('name', 'N/A'))}")
        print(f"Confidence      : {result.get('confidence', 0)}%")
        print(f"Grad-CAM        : {'YES' if result.get('gradcam_base64') else 'NO'}")
        print(f"Demo mode       : {result.get('demo_mode', 'N/A')}")
        print(f"Is toxic        : {result.get('is_toxic', 'N/A')}")
        med = result.get('medicinal_info', {})
        print(f"Medicinal uses  : {str(med.get('uses', med.get('medicinal_uses', 'N/A')))[:60]}")
    except Exception as e:
        print(f"Prediction      : FAILED - {e}")
else:
    print("No test image found in merged dataset! Prediction skipped.")

# 4. Vercel live site check
print()
r = requests.get("https://plantoai.vercel.app", timeout=30)
has_demo = "demo mode" in r.text.lower()
has_226 = "226" in r.text
has_80 = ">80<" in r.text or "80 M" in r.text
print(f"Vercel site     : {r.status_code}")
print(f"Demo banner     : {'STILL SHOWING - FIX NEEDED' if has_demo else 'GONE - GOOD'}")
print(f"Stats (226)     : {'STILL WRONG - FIX NEEDED' if has_226 else 'FIXED - GOOD'}")

print()
print("="*50)
print("ACTION ITEMS:")
if r.status_code != 200:
    print("- Vercel site down")
print("Check above results and fix any FAILED items")
print("="*50)
