import tensorflow as tf
import numpy as np
import os
from PIL import Image
import io
import json
from collections import Counter

MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\mobilenetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def reconstruct_mapping():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found.")
        return
        
    print("🧠 Loading Master Model...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    print(f"📁 Analyzing {len(folders)} folders...")
    
    mapping = {} # folder_name -> list of best indices
    
    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:5]
        if not images:
            continue
            
        indices = []
        for img_name in images:
            img_path = os.path.join(folder_path, img_name)
            try:
                img = Image.open(img_path).convert('RGB').resize((224, 224))
                img_array = np.array(img, dtype=np.float32)
                img_array = (img_array / 127.5) - 1.0
                img_array = np.expand_dims(img_array, axis=0)
                
                preds = model.predict(img_array, verbose=0)
                indices.append(int(np.argmax(preds[0])))
            except:
                continue
        
        if indices:
            # Get the most common index
            most_common = Counter(indices).most_common(1)[0][0]
            mapping[folder] = most_common
            print(f"📁 {folder:25} -> Index {most_common}")

    # Create the 0-79 list
    # Because some folders might map to same index if model is poor, 
    # and some indices might be missing. 
    # But for a "Best" model, it should be 1-to-1.
    
    final_list = ["Unknown"] * 80
    for folder, idx in mapping.items():
        if idx < 80:
            final_list[idx] = folder
            
    # Check for duplicates or missing
    unmapped_indices = [i for i, v in enumerate(final_list) if v == "Unknown"]
    if unmapped_indices:
        print(f"⚠️ Unmapped indices: {unmapped_indices}")
        
    with open("reconstructed_classes.json", "w") as f:
        json.dump(final_list, f, indent=2)
    print("\n📦 Saved reconstructed_classes.json")

if __name__ == "__main__":
    reconstruct_mapping()
