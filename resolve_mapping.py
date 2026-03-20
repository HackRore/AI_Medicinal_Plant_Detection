import tensorflow as tf
import numpy as np
import os
from PIL import Image
import json
from collections import Counter

MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\mobilenetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

PRIORITY_PLANTS = [
    "Aloevera", "Tulsi", "Neem", "Turmeric", "Amruthaballi",
    "Amla", "Ashwagandha", "Betel", "Bhrami", "Bringaraja",
    "Caricature", "Castor", "Curry", "Doddpathre", "Drumstick",
    "Ekka", "Ginger", "Guava", "Hibiscus", "Henna",
    "Insulin", "Jackfruit", "Jasmine", "Lemon", "Lemongrass",
    "Mango", "Marigold", "Mint", "Nelavembu", "Nerale",
    "Nooni", "Onion", "Papaya", "Parijatha", "Pepper",
    "Pomoegranate", "Pumpkin", "Raddish", "Rose", "Sampige",
    "Sapota", "Spinach", "Tamarind", "Taro", "Tecoma",
    "Thumbe", "Tomato", "Vitamin", "Wood_sorel"
]

def resolve_mapping():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found.")
        return
        
    print(f"🧠 Loading Model for Resolution: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    folders = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    
    index_to_candidates = {} # {0: ["Aloevera"], 3: ["Arali", "Tulsi"]}
    
    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:3]
        if not images: continue
            
        indices = []
        for img_name in images:
            img_path = os.path.join(folder_path, img_name)
            try:
                img = Image.open(img_path).convert('RGB').resize((224, 224))
                img_array = np.array(img, dtype=np.float32)
                
                # MobileNetV2 Expects [-1, 1]
                img_array = (img_array / 127.5) - 1.0
                
                img_array = np.expand_dims(img_array, axis=0) 
                
                preds = model.predict(img_array, verbose=0)
                idx = int(np.argmax(preds[0]))
                indices.append(idx)
            except:
                continue
        
        if indices:
            # Majority vote for this folder
            best_idx = Counter(indices).most_common(1)[0][0]
            if best_idx not in index_to_candidates:
                index_to_candidates[best_idx] = []
            index_to_candidates[best_idx].append(folder)
            print(f"📁 {folder} -> Index {best_idx}")

    # Resolve
    final_list = ["Unknown / Non-Medicinal"] * 80
    
    print("\n⚔️ Resolving Collisions...")
    for idx, candidates in index_to_candidates.items():
        if idx >= 80: continue
        
        winner = candidates[0]
        if len(candidates) > 1:
            print(f"⚠️ Conflict at {idx}: {candidates}")
            # Find highest priority
            found_priority = False
            for p in PRIORITY_PLANTS:
                # Case insensitive check
                matches = [c for c in candidates if p.lower().replace(" ", "") in c.lower().replace(" ", "") or c.lower() in p.lower()]
                if matches:
                    winner = matches[0]
                    found_priority = True
                    break
            
            if found_priority:
                print(f"   🏆 Winner (Priority): {winner}")
            else:
                print(f"   🎲 Winner (First): {winner}")
        
        final_list[idx] = winner

    with open(r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json", "w") as f:
        json.dump(final_list, f, indent=2)
    print("✅ Resolved Mapping Saved to Backend!")

if __name__ == "__main__":
    resolve_mapping()
