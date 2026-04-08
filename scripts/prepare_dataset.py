import os
import shutil
from pathlib import Path

# THE 12 MEDICINAL CLASSES FOUND IN OUR CACHE (Aligned with Knowledge Base)
APPROVED_CLASSES = [
    "Alstonia Scholaris", "Arjun", "Bael", "Basil", "Chinar", 
    "Gauva", "Jamun", "Jatropha", "Lemon", "Mango", 
    "Pomegranate", "Pongamia Pinnata"
]

DATASET_ROOT = Path("dataset/unified_dataset")
# SOURCE: Kaggle Hub cache for hmohamedhussain
SRC_KAGGE = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets\hmohamedhussain\leaves-image-dataset\versions\1\train\train")

def prepare():
    total = 0
    # CLEAN PREVIOUS RUN
    if DATASET_ROOT.exists():
        shutil.rmtree(DATASET_ROOT)
    DATASET_ROOT.mkdir(parents=True)
    
    for cls in APPROVED_CLASSES:
        target_dir = DATASET_ROOT / cls.replace(" ", "_")
        target_dir.mkdir(exist_ok=True)
        count = 0
        src = SRC_KAGGE / cls
        if src.exists():
            for img in src.iterdir():
                if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    shutil.copy2(img, target_dir / f"kag_{img.name}")
                    count += 1
                    total += 1
        print(f"Purified {cls}: {count} images collected.")
    print(f"\nTOTAL IMAGES COLLECTED: {total}")

if __name__ == "__main__":
    prepare()
    print("DATASET PURIFICATION COMPLETE. ALL CROP NOISE PURGED.")
