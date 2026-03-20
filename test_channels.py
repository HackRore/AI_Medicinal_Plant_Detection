import tensorflow as tf
import numpy as np
import os
from PIL import Image
import json

MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def test_channels():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found.")
        return
        
    print(f"🧠 Loading Enhanced Model: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    # Test with Aloevera (Index 0 in dict)
    folder = "Aloevera"
    path = os.path.join(DATA_DIR, folder)
    images = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    img_path = os.path.join(path, images[0])
    
    img = Image.open(img_path).convert('RGB').resize((224, 224))
    img_rgb = np.array(img, dtype=np.float32)
    img_bgr = img_rgb[:, :, ::-1] # Swaps Channel
    
    # Test RGB
    p_rgb = model.predict(np.expand_dims(img_rgb, 0), verbose=0)
    idx_rgb = np.argmax(p_rgb[0])
    conf_rgb = p_rgb[0][idx_rgb]
    
    # Test BGR
    p_bgr = model.predict(np.expand_dims(img_bgr, 0), verbose=0)
    idx_bgr = np.argmax(p_bgr[0])
    conf_bgr = p_bgr[0][idx_bgr]
    
    print(f"🌈 RGB Test: Index {idx_rgb} (Conf: {conf_rgb*100:.1f}%)")
    print(f"🌈 BGR Test: Index {idx_bgr} (Conf: {conf_bgr*100:.1f}%)")

if __name__ == "__main__":
    test_channels()
