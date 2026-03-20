import tensorflow as tf
import numpy as np
import os
from PIL import Image
import json

MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def deep_trace():
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    # Test Aloevera
    img_path = os.path.join(DATA_DIR, "Aloevera", os.listdir(os.path.join(DATA_DIR, "Aloevera"))[0])
    img = Image.open(img_path).convert('RGB').resize((224, 224))
    img_array = np.array(img, dtype=np.float32)
    # NO SCALING - RAW [0, 255]
    
    preds = model.predict(np.expand_dims(img_array, 0), verbose=0)
    idx = np.argmax(preds[0])
    print(f"🎯 Aloevera image -> Predicted Index: {idx}")
    
    # Test Neem
    img_path = os.path.join(DATA_DIR, "Neem", os.listdir(os.path.join(DATA_DIR, "Neem"))[0])
    img = Image.open(img_path).convert('RGB').resize((224, 224))
    img_array = np.array(img, dtype=np.float32)
    preds = model.predict(np.expand_dims(img_array, 0), verbose=0)
    idx = np.argmax(preds[0])
    print(f"🎯 Neem image -> Predicted Index: {idx}")

if __name__ == "__main__":
    deep_trace()
