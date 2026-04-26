import numpy as np
import onnxruntime as ort
from PIL import Image
import os, json

MODEL_PATH = r"d:\PROJECT FINAL\backend\ml_models\plantoai_model.onnx"
CLASS_PATH = r"d:\PROJECT FINAL\backend\app\data\class_names.json"
IMG_DIR = r"d:\PROJECT FINAL\dataset\IMLD\test\images"

with open(CLASS_PATH) as f: 
    classes = json.load(f)
    
sess = ort.InferenceSession(MODEL_PATH)
input_name = sess.get_inputs()[0].name

files = [f for f in os.listdir(IMG_DIR) if f.endswith(".jpg")][:10]

print("Batch Test Results:")
print("-" * 30)

for f in files:
    path = os.path.join(IMG_DIR, f)
    img = Image.open(path).convert("RGB").resize((224, 224))
    
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    x = (np.array(img).astype(np.float32) / 255.0 - mean) / std
    x = np.transpose(x, (2, 0, 1)).reshape(1, 3, 224, 224)
    
    logits = sess.run(None, {input_name: x})[0][0]
    preds = np.exp(logits - np.max(logits))
    preds = preds / preds.sum()
    idx = np.argmax(preds)
    
    c_raw = classes[idx]
    c_name = c_raw["name"] if isinstance(c_raw, dict) else c_raw
    print(f"{f}: {c_name} ({round(preds[idx]*100, 1)}%)")
