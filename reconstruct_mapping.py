import tensorflow as tf
import numpy as np
import os
from PIL import Image
import io
import json

MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\mobilenetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def reconstruct_mapping():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found.")
        return
        
    print("🧠 Loading Master Model...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    print(f"📁 Found {len(folders)} folders.")
    
    mapping = {} # index -> folder_name
    
    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            continue
            
        img_path = os.path.join(folder_path, images[0])
        try:
            # Preprocess
            img = Image.open(img_path).convert('RGB').resize((224, 224))
            img_array = np.array(img, dtype=np.float32)
            img_array = (img_array / 127.5) - 1.0 # Standard MobileNet normalization
            img_array = np.expand_dims(img_array, axis=0)
            
            # Predict
            preds = model.predict(img_array, verbose=0)
            best_idx = int(np.argmax(preds[0]))
            conf = float(preds[0][best_idx])
            
            mapping[best_idx] = folder
            print(f"🔍 Folder: {folder:20} -> Index: {best_idx} ({conf*100:.1f}%)")
        except Exception as e:
            print(f"❌ Error testing {folder}: {e}")

    # Generate the final sorted list based on indices 0-79
    final_list = [None] * 80
    for i in range(80):
        final_list[i] = mapping.get(i, f"Unknown_{i}")
        
    print("\n✅ Reconstruction Complete!")
    print(json.dumps(final_list, indent=2))
    
    with open("reconstructed_classes.json", "w") as f:
        json.dump(final_list, f, indent=2)

if __name__ == "__main__":
    reconstruct_mapping()
