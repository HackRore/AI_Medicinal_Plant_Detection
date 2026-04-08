import os
from pathlib import Path

def find_species_roots():
    base_cache = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets")
    print(f"🔍 SEARCHING CACHE: {base_cache}")
    
    for root, dirs, files in os.walk(base_cache):
        # A species root has at least 50 images in subfolders
        if len(dirs) > 5:
            # Check if one of the subdirs has images
            first_sub = Path(root) / dirs[0]
            images = list(first_sub.glob("*.jpg")) + list(first_sub.glob("*.png"))
            if len(images) > 0:
                print(f"🎯 FOUND ROOT: {root} ({len(dirs)} classes)")

if __name__ == "__main__":
    find_species_roots()
