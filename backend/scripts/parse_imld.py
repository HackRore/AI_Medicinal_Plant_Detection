"""
PlantoAI Data Forge: IMLD (PlantDoc) Parser.
Converts YOLO-formatted object detection data into classification leaf crops.
"""
import os, cv2, yaml, numpy as np
from tqdm import tqdm
from pathlib import Path

ROOT        = r"D:\PROJECT FINAL"
IMLD_DIR    = os.path.join(ROOT, "dataset", "IMLD")
UNIFIED_DIR = os.path.join(ROOT, "dataset", "unified_dataset")
YAML_PATH   = os.path.join(IMLD_DIR, "data.yaml")

def parse():
    print("Initializing IMLD Forge...")
    with open(YAML_PATH, 'r') as f:
        config = yaml.safe_load(f)
    classes = config['names']
    
    # Process train, valid, and test
    for split in ['train', 'valid', 'test']:
        img_dir = os.path.join(IMLD_DIR, split, "images")
        lbl_dir = os.path.join(IMLD_DIR, split, "labels")
        
        if not os.path.exists(img_dir): continue
        
        files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"Processing {split} split ({len(files)} images)...")
        
        for f in tqdm(files):
            img_path = os.path.join(img_dir, f)
            lbl_path = os.path.join(lbl_dir, os.path.splitext(f)[0] + ".txt")
            
            if not os.path.exists(lbl_path): continue
            
            img = cv2.imread(img_path)
            if img is None: continue
            h, w, _ = img.shape
            
            with open(lbl_path, 'r') as lf:
                for line in lf:
                    parts = line.strip().split()
                    if len(parts) != 5: continue
                    
                    cls_idx = int(parts[0])
                    cls_name = classes[cls_idx].replace(" ", "_")
                    xc, yc, nw, nh = map(float, parts[1:])
                    
                    # Convert YOLO to Pixel coordinates
                    x1 = int((xc - nw/2) * w)
                    y1 = int((yc - nh/2) * h)
                    x2 = int((xc + nw/2) * w)
                    y2 = int((yc + nh/2) * h)
                    
                    # Sanity bounds
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    
                    if (x2 - x1) < 10 or (y2 - y1) < 10: continue
                    
                    crop = img[y1:y2, x1:x2]
                    
                    # Save to unified dataset
                    out_dir = os.path.join(UNIFIED_DIR, cls_name)
                    os.makedirs(out_dir, exist_ok=True)
                    
                    out_name = f"imld_{split}_{os.path.splitext(f)[0]}_{np.random.randint(10000)}.jpg"
                    cv2.imwrite(os.path.join(out_dir, out_name), crop)

    print("Data Forge Complete. IMLD crops merged into unified_dataset.")

if __name__ == "__main__":
    parse()
