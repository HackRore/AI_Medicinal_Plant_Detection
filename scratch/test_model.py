import onnxruntime as ort
import numpy as np
from PIL import Image
import os
import json
from io import BytesIO

MODEL_PATH = 'backend/ml_models/plantoai_model.onnx'
CLASS_PATH = 'backend/app/data/class_names.json'

def predict(image_path):
    sess = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    with open(CLASS_PATH, encoding='utf-8') as f:
        class_names = json.load(f)
    
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    
    x = np.array(img).astype(np.float32) / 255.0
    x = np.transpose(x, (2, 0, 1))
    x = np.expand_dims(x, axis=0)
    
    input_name = sess.get_inputs()[0].name
    raw_preds = sess.run(None, {input_name: x})[0][0]
    
    exp_preds = np.exp(raw_preds - np.max(raw_preds))
    preds = exp_preds / exp_preds.sum()
    
    idx = int(np.argmax(preds))
    conf = float(preds[idx])
    
    name = class_names[idx]['name'] if isinstance(class_names[idx], dict) else class_names[idx]
    
    return name, conf

if __name__ == "__main__":
    test_dir = 'test_images'
    for img_file in os.listdir(test_dir):
        if img_file.endswith(('.jpg', '.png')):
            path = os.path.join(test_dir, img_file)
            name, conf = predict(path)
            print(f"{img_file}: {name} ({conf*100:.2f}%)")
