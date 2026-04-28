import os
import shutil
from tqdm import tqdm
import re

def standardize_name(name):
    # Remove underscores, numbers, and common suffixes
    name = name.replace('_', ' ').strip()
    name = re.sub(r'\d+', '', name).strip()
    # Title Case (e.g., 'neem leaf' -> 'Neem Leaf')
    return name.title()

def unify_dataset(src_root, dest_root):
    if os.path.exists(dest_root):
        shutil.rmtree(dest_root)
    os.makedirs(dest_root)
    
    print(f"Starting Neural Unification from {src_root} to {dest_root}...")
    
    stats = {}
    
    # We want to find folders that contain images, and use their parent/name as class
    for root, dirs, files in os.walk(src_root):
        # Filter for image files
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if image_files:
            # The class name is the name of the folder containing these images
            folder_name = os.path.basename(root)
            
            # Skip generic folder names
            if folder_name.lower() in ['train', 'val', 'test', 'images', 'labels', 'dataset', 'raw', 'unified', 'master_dataset']:
                # Use the parent folder instead
                folder_name = os.path.basename(os.path.dirname(root))
            
            clean_name = standardize_name(folder_name)
            
            # Create destination folder
            class_dest = os.path.join(dest_root, clean_name)
            os.makedirs(class_dest, exist_ok=True)
            
            for f in image_files:
                src_path = os.path.join(root, f)
                # Avoid filename collisions
                dest_filename = f"{len(os.listdir(class_dest))}_{f}"
                dest_path = os.path.join(class_dest, dest_filename)
                
                try:
                    shutil.copy2(src_path, dest_path)
                    stats[clean_name] = stats.get(clean_name, 0) + 1
                except Exception as e:
                    pass

    print("\n=== UNIFICATION COMPLETE ===")
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    for name, count in sorted_stats:
        print(f"{name}: {count} images")
    
    print(f"\nTotal Classes Unified: {len(stats)}")
    print(f"Total Images in Monolith: {sum(stats.values())}")

if __name__ == "__main__":
    unify_dataset('dataset', 'dataset/FINAL_MONOLITH')
