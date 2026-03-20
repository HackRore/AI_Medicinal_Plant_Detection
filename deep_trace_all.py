import tensorflow as tf
import numpy as np
import os
from PIL import Image
import json
from collections import Counter

# Use the 90MB model
MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def deep_trace_all():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found.")
        return
        
    print(f"🧠 Loading Enhanced Model: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    folders = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    print(f"📁 Analyzing {len(folders)} folders...")
    
    final_mapping = ["Unknown"] * 80
    
    conflict_count = 0
    
    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:3]
        if not images:
            continue
            
        indices = []
        for img_name in images:
            img_path = os.path.join(folder_path, img_name)
            try:
                # Same preprocessing as MLService
                img = Image.open(img_path).convert('RGB').resize((224, 224))
                img_array = np.array(img, dtype=np.float32)
                # Keras EfficientNetV2 expects [0, 255] usually
                # We verified earlier that RGB order is better than BGR
                # We verified earlier that [0, 255] works for Index 0 (Aloevera)
                
                img_array = np.expand_dims(img_array, axis=0)
                
                preds = model.predict(img_array, verbose=0)
                idx = int(np.argmax(preds[0]))
                indices.append(idx)
            except:
                continue
        
        if indices:
            most_common = Counter(indices).most_common(1)[0][0]
            
            # Check for collision
            if most_common < 80:
                if final_mapping[most_common] != "Unknown":
                    print(f"⚠️ Collision at Index {most_common}: {final_mapping[most_common]} vs {folder}")
                    conflict_count += 1
                
                final_mapping[most_common] = folder
                print(f"📁 {folder:25} -> Index {most_common}")
            else:
                 print(f"⚠️ Out of bounds Index {most_common} for {folder}")

    # Fill unknowns with something generic if needed, or leave as Unknown
    
    print(f"\n✅ Mapping Complete. {conflict_count} Collisions.")
    
    with open("deep_trace_mapping.json", "w") as f:
        json.dump(final_mapping, f, indent=2)
    print("📦 Saved deep_trace_mapping.json")

if __name__ == "__main__":
    deep_trace_all()
