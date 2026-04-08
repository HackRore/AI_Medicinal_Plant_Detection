import os
from pathlib import Path

def find_leaf_folders():
    base_cache = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets")
    print(f"🕵️  DEEP SCAN: {base_cache}")
    
    for root, dirs, files in os.walk(base_cache):
        # Relax constraints: any folder with > 5 images might be a species
        if len(files) > 5:
            # Check for image extensions (case insensitive)
            img_count = sum(1 for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
            if img_count > 5:
                print(f"🌿 MATCH: {root} ({img_count} images)")

if __name__ == "__main__":
    find_leaf_folders()
