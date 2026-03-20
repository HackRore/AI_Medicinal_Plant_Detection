import tensorflow as tf
import numpy as np
import os
from PIL import Image
import json
from collections import Counter

# Use the 90MB model
MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def reconstruct_mapping_final():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found.")
        return
        
    print(f"🧠 Loading Enhanced Model: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    print(f"📁 Analyzing {len(folders)} folders...")
    
    # Store empirical index for each folder
    results = [] # list of (folder, index, confidence)
    
    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:3]
        if not images:
            continue
            
        indices = []
        confs = []
        for img_name in images:
            img_path = os.path.join(folder_path, img_name)
            try:
                img = Image.open(img_path).convert('RGB').resize((224, 224))
                img_array = np.array(img, dtype=np.float32)
                # DO NOT SCALE TO [-1, 1] IF MODEL EXPECTS [0, 255]
                # Actually, let's try raw [0, 255] first as it's common for EfficientNetV2 Keras
                img_array = np.expand_dims(img_array, axis=0)
                
                preds = model.predict(img_array, verbose=0)
                idx = int(np.argmax(preds[0]))
                conf = float(preds[0][idx])
                indices.append(idx)
                confs.append(conf)
            except:
                continue
        
        if indices:
            most_common = Counter(indices).most_common(1)[0][0]
            avg_conf = sum(confs)/len(confs)
            results.append((folder, most_common, avg_conf))
            print(f"📁 {folder:25} -> Index {most_common:2} ({avg_conf*100:4.1f}%)")

    # Construct the 80-item list
    final_list = ["Unknown / Non-Medicinal"] * 80
    for folder, idx, conf in results:
        if idx < 80:
            final_list[idx] = folder
            
    with open("final_ordered_classes.json", "w") as f:
        json.dump(final_list, f, indent=2)
    print("\n📦 Saved final_ordered_classes.json")

if __name__ == "__main__":
    reconstruct_mapping_final()
