import requests
import os

# Test live Render backend directly
API = "https://plantoai-backend.onrender.com/api/v1/predict/"

# Use a real dataset image
DATASET = r'd:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset'
test_img = None
for root, dirs, files in os.walk(DATASET):
    for f in files:
        if f.lower().endswith('.jpg'):
            test_img = os.path.join(root, f)
            break
    if test_img:
        break

print(f"Testing live API with: {test_img}")
with open(test_img, 'rb') as f:
    response = requests.post(
        API,
        files={'file': (os.path.basename(test_img), f, 'image/jpeg')},
        timeout=60
    )

if response.status_code == 200:
    r = response.json()
    print(f"Plant   : {r.get('predicted_class', 'N/A')}")
    print(f"Conf    : {r.get('confidence', 0)*100:.1f}%")
    print(f"GradCAM : {'YES' if r.get('gradcam_base64') else 'NO'}")
    print(f"Toxic   : {r.get('is_toxic', False)}")
    print("LIVE SITE AI IS WORKING!")
else:
    print(f"FAILED: {response.status_code} — {response.text}")
