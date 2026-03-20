import tensorflow as tf
import numpy as np
import os
from PIL import Image
import json

MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\mobilenetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def verify_17mb():
    # Alphabetical order as used by Keras
    folders = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    
    print(f"🧠 Testing Master Model: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    test_cases = ["Aloevera", "Amla", "Beans", "Tulsi", "Turmeric"]
    
    for folder in test_cases:
        actual_idx = folders.index(folder)
        path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:1]
        
        img = Image.open(os.path.join(path, images[0])).convert('RGB').resize((224, 224))
        img_array = np.array(img, dtype=np.float32)
        img_array = (img_array / 127.5) - 1.0 # 17MB model expects [-1, 1] usually
        img_array = np.expand_dims(img_array, axis=0)
        
        preds = model.predict(img_array, verbose=0)
        top_idx = int(np.argmax(preds[0]))
        
        print(f"📁 Folder: {folder:12} | Exp. Idx: {actual_idx:2} | Pred. Idx: {top_idx:2} | {'✅' if actual_idx == top_idx else '❌'}")

if __name__ == "__main__":
    verify_17mb()
