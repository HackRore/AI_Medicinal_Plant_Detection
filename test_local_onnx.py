"""
Direct local inference test — bypasses Render completely.
Tests whether the ONNX model on disk actually works.
"""
import onnxruntime as ort
import numpy as np
import json
import os
import requests
from PIL import Image
from io import BytesIO

ONNX_PATH  = "backend/ml_models/plantoai_model.onnx"
CLASS_PATH = "backend/app/data/class_names.json"
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

print("=== LOCAL ONNX INFERENCE TEST ===")
print(f"ONNX: {os.path.getsize(ONNX_PATH)/1024/1024:.1f}MB")
data_path = ONNX_PATH + ".data"
if os.path.exists(data_path):
    print(f"DATA: {os.path.getsize(data_path)/1024/1024:.1f}MB")

with open(CLASS_PATH) as f:
    class_names = json.load(f)
print(f"Classes: {len(class_names)} — {class_names[:5]}...")

sess = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
print(f"Input: {sess.get_inputs()[0].name} shape={sess.get_inputs()[0].shape}")

def predict_bytes(img_bytes, label):
    img = Image.open(BytesIO(img_bytes)).convert("RGB").resize((224, 224))
    x = np.array(img, dtype=np.float32) / 255.0
    x = (x - MEAN) / STD
    x = np.transpose(x, (2, 0, 1))[np.newaxis]
    out = sess.run(None, {sess.get_inputs()[0].name: x})[0][0]
    probs = np.exp(out - out.max())
    probs /= probs.sum()
    top3 = np.argsort(probs)[-3:][::-1]
    print(f"\n  [{label}]")
    for idx in top3:
        print(f"    {class_names[idx]:25s}: {probs[idx]*100:.2f}%")

# Test 1: Download real Neem leaf
print("\nDownloading real leaf images from iNaturalist...")
headers = {"User-Agent": "PlantoAI-LocalTest/1.0"}
test_images = [
    ("Neem leaf (iNaturalist)",   "https://inaturalist-open-data.s3.amazonaws.com/photos/169358846/medium.jpg"),
    ("Tulsi leaf (iNaturalist)",  "https://inaturalist-open-data.s3.amazonaws.com/photos/102921891/medium.jpg"),
]

for label, url in test_images:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            predict_bytes(r.content, label)
        else:
            print(f"  {label}: download failed {r.status_code}")
    except Exception as e:
        print(f"  {label}: {e}")

# Test 2: Solid colors (must give low confidence)
print("\nTesting solid color rejection...")
for color, name in [((34,139,34),"Solid Green"), ((200,50,50),"Solid Red"), ((50,100,200),"Solid Blue")]:
    img = Image.new("RGB", (224,224), color=color)
    buf = BytesIO()
    img.save(buf, "JPEG")
    predict_bytes(buf.getvalue(), name)

print("\n=== LOCAL TEST COMPLETE ===")
