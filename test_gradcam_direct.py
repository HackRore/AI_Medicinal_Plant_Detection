import requests
import base64
import os
from PIL import Image
import io

# Find one good plant image
DATASET_DIR = r'd:\PROJECT STAGE 1\dataset'
test_img = None
for root, dirs, files in os.walk(DATASET_DIR):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg')):
            test_img = os.path.join(root, f)
            break
    if test_img:
        break

print(f"Testing Grad-CAM with: {test_img}")

with open(test_img, 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:8000/api/v1/predict/',
        files={'file': (os.path.basename(test_img), f, 'image/jpeg')},
        timeout=60
    )

result = response.json()
print(f"Plant    : {result.get('predicted_class')}")
print(f"Conf     : {result.get('confidence')}%")
print(f"GradCAM  : {'PRESENT' if result.get('gradcam_base64') else 'MISSING'}")

if result.get('gradcam_base64'):
    # Save heatmap image
    heatmap_data = base64.b64decode(result['gradcam_base64'])
    heatmap_img = Image.open(io.BytesIO(heatmap_data))
    save_path = os.path.abspath(r'd:\PROJECT STAGE 1\gradcam_final.jpg')
    heatmap_img.save(save_path)
    print(f"Grad-CAM heatmap saved to: {save_path}")
    print(f"File exists after save? {os.path.exists(save_path)}")
    print(f"File size: {os.path.getsize(save_path)} bytes")
    print("OPEN THIS FILE to see if heatmap looks correct!")
else:
    print("WARNING: Grad-CAM not working — debug needed")
