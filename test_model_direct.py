import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
import glob

# Load model
model = tf.keras.models.load_model(
    r'd:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5'
)
with open(r'd:\PROJECT STAGE 1\backend\ml_models\class_names.json') as f:
    classes = json.load(f)

print(f"Model loaded: {len(classes)} classes")
print("="*60)

# Find test images from dataset
DATASET_DIR = r'd:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset'
test_results = []

# Pick 2 images from each of 10 different plant folders
plant_folders = []
for root, dirs, files in os.walk(DATASET_DIR):
    images = [f for f in files if f.lower().endswith(('.jpg','.jpeg','.png'))]
    if len(images) >= 5:
        plant_folders.append((root, images))

# Test 10 different plants
tested = 0
correct = 0

for folder_path, images in plant_folders[:10]:
    plant_folder_name = os.path.basename(folder_path)
    test_image = os.path.join(folder_path, images[0])

    try:
        # Match production: RGB, BILINEAR, [0, 255] float32 NHWC
        img = Image.open(test_image).convert('RGB').resize((224,224), resample=Image.BILINEAR)
        arr = np.expand_dims(np.array(img, dtype=np.float32), axis=0)
        preds = model.predict(arr, verbose=0)

        top3_idx = np.argsort(preds[0])[-3:][::-1]
        top1_name = classes[top3_idx[0]]
        top1_conf = preds[0][top3_idx[0]] * 100
        top2_name = classes[top3_idx[1]]
        top2_conf = preds[0][top3_idx[1]] * 100
        top3_name = classes[top3_idx[2]]
        top3_conf = preds[0][top3_idx[2]] * 100

        # Check if correct plant name is in folder name
        is_correct = plant_folder_name.lower() in top1_name.lower() or top1_name.lower() in plant_folder_name.lower()
        if is_correct:
            correct += 1
        tested += 1

        status = "CORRECT" if is_correct else "WRONG"
        print(f"\nPlant folder : {plant_folder_name}")
        print(f"Predicted #1 : {top1_name} ({top1_conf:.1f}%) [{status}]")
        print(f"Predicted #2 : {top2_name} ({top2_conf:.1f}%)")
        print(f"Predicted #3 : {top3_name} ({top3_conf:.1f}%)")
        print(f"Image tested : {os.path.basename(test_image)}")

        test_results.append({
            "folder": plant_folder_name,
            "predicted": top1_name,
            "confidence": float(round(top1_conf, 1)),
            "correct": bool(is_correct)
        })

    except Exception as e:
        print(f"ERROR on {plant_folder_name}: {e}")

print("\n" + "="*60)
print(f"RESULTS: {correct}/{tested} correct")
print(f"Accuracy on test: {correct/tested*100:.1f}%")
print("="*60)

# Save results
with open(r'd:\PROJECT STAGE 1\test_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)
print("Results saved to test_results.json")
