import tensorflow as tf
import numpy as np
import os
from PIL import Image
import json
from collections import Counter

# Explicitly target the 17MB Master Model
MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\mobilenetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"
OUTPUT_JSON = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"

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

def force_align():
    print(f"🔧 Forcing Alignment using Model: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    folders = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    
    # Initialize logic
    mapping = ["Unknown"] * 80
    index_hits = {} # idx -> list of folders
    
    for folder in folders:
        folder_path = os.path.join(DATA_DIR, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:5] # Test 5 images
        
        preds = []
        for img_name in images:
            try:
                img = Image.open(os.path.join(folder_path, img_name)).convert('RGB').resize((224, 224), resample=Image.BILINEAR)
                arr = (np.array(img, dtype=np.float32) / 127.5) - 1.0
                arr = np.expand_dims(arr, 0)
                p = model.predict(arr, verbose=0)
                preds.append(np.argmax(p[0]))
            except: pass
            
        if preds:
            # Majority vote
            common = Counter(preds).most_common(1)[0][0]
            if common not in index_hits: index_hits[common] = []
            index_hits[common].append(folder)
            print(f"   📂 {folder} -> {common}")
            
    # Resolve
    print("\n⚔️ Resolving...")
    for idx, candidates in index_hits.items():
        if idx >= 80: continue
        
        winner = candidates[0]
        if len(candidates) > 1:
            # Priority check
            prioritized = [c for c in candidates if c in PRIORITY_PLANTS]
            if prioritized: winner = prioritized[0]
            print(f"   ⚠️ Conflict at {idx}: {candidates} -> Winner: {winner}")
            
        mapping[idx] = winner
        
    # Write
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(mapping, f, indent=2)
        
    print(f"✅ Written to {OUTPUT_JSON}")
    
    # Verify exact file content for key species
    print("🔍 Verification Check:")
    print(f"   Index 0: {mapping[0]}")
    print(f"   Index 12: {mapping[12]}")
    print(f"   Index 54: {mapping[54]}")

if __name__ == "__main__":
    force_align()
