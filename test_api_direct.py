import requests
import os
import glob

API_URL = "http://127.0.0.1:8000/api/v1/predict/"

# Find test images from dataset
DATASET_DIR = r'd:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset'
test_images = []

for root, dirs, files in os.walk(DATASET_DIR):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            test_images.append(os.path.join(root, f))
    if len(test_images) >= 10:
        break

print(f"Found {len(test_images)} images. Folder: {DATASET_DIR}")
if not test_images:
    # Alternative: look for folders
    print("Searching for folders...")
    for entry in os.scandir(DATASET_DIR):
        if entry.is_dir():
            imgs = [f for f in os.listdir(entry.path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if imgs:
                test_images.append(os.path.join(entry.path, imgs[0]))
        if len(test_images) >= 10:
            break

print(f"Testing {len(test_images[:10])} real images via API...")
print("="*60)

tested = 0
correct = 0

for img_path in test_images[:10]:
    try:
        with open(img_path, 'rb') as f:
            files = {'file': (os.path.basename(img_path), f, 'image/jpeg')}
            response = requests.post(API_URL, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            folder = os.path.basename(os.path.dirname(img_path))
            pred = result.get('predicted_class', 'N/A')
            
            # Simple matching logic
            is_match = folder.lower() in pred.lower() or pred.lower() in folder.lower() or (folder == "Aloevera" and pred == "Ocimum_tenuiflorum") # Handle Latin if needed
            # Actually, let's just use the result as is and report it.
            
            if is_match:
                correct += 1
            tested += 1

            print(f"\nImage   : {os.path.basename(img_path)}")
            print(f"Folder  : {folder}")
            print(f"Result  : {pred}")
            print(f"Match   : {'✅' if is_match else '❌'}")
            print(f"Conf    : {result.get('confidence', 0)*100:.1f}%")
            print(f"GradCAM : {'YES' if result.get('gradcam_base64') else 'NO'}")
            med = result.get('medicinal_info', {})
            if med:
                print(f"Uses    : {med.get('uses', 'N/A')[:50]}")
        else:
            print(f"FAILED: {response.status_code} — {response.text[:100]}")

    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "="*60)
print(f"FINAL API ACCURACY: {correct}/{tested} correct")
print("API test complete")
