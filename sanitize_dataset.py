import os
from PIL import Image, ImageFile
from tqdm import tqdm

ImageFile.LOAD_TRUNCATED_IMAGES = False # We want to catch them!

def sanitize_dataset(root_dir):
    print(f"🚀 Initializing Neural Sanitizer for {root_dir}...")
    corrupted_count = 0
    total_scanned = 0
    
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                total_scanned += 1
                path = os.path.join(root, f)
                try:
                    with Image.open(path) as img:
                        img.verify() # Verify file integrity
                    # Re-open and try to load (verify() doesn't catch everything)
                    with Image.open(path) as img:
                        img.load()
                except Exception as e:
                    print(f"  ❌ Deleting Corrupted: {f} | Reason: {e}")
                    os.remove(path)
                    corrupted_count += 1
                    
    print(f"\n=== SANITIZATION COMPLETE ===")
    print(f"Total Scanned: {total_scanned}")
    print(f"Total Deleted: {corrupted_count}")
    print(f"Healthy Images: {total_scanned - corrupted_count}")

if __name__ == "__main__":
    sanitize_dataset('dataset/FINAL_MONOLITH')
