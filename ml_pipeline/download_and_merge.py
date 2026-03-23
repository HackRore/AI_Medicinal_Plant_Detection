import kagglehub
import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 Starting dataset download and merge...")

# Download datasets
print("📥 Downloading datasets...")
path1 = kagglehub.dataset_download("rizkikecek/dataset-herbal-leaves")
path2 = kagglehub.dataset_download("mirlab/medleaves-medicinal-plant-leaves-dataset")
path3 = kagglehub.dataset_download("kagglenou2023/medicinal-plants")
path4 = kagglehub.dataset_download("csafrit2/plant-leaves-for-image-classification")  # optional

DATASETS = [path1, path2, path3]  # skip 4th large

print("Downloaded paths:")
for i, p in enumerate(DATASETS, 1):
    print(f"{i}. {p}")

# Merged dir (project relative)
MERGED_DIR = Path("dataset/merged_dataset")
MERGED_DIR.mkdir(exist_ok=True, parents=True)

class_counts = {}

for dataset_idx, dataset_path in enumerate(DATASETS, 1):
    logger.info(f"Merging dataset {dataset_idx}: {dataset_path}")
    dataset_path = Path(dataset_path)
    dataset_prefix = dataset_path.parent.name[:4].upper() + "_"
    for root, dirs, _ in os.walk(dataset_path):
        for dir_name in dirs:
            class_src = Path(root) / dir_name
            try:
                images = [f for f in os.listdir(class_src) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            except:
                continue
            if len(images) > 10:
                class_dst = MERGED_DIR / dir_name
                class_dst.mkdir(exist_ok=True)
                copied = 0
                for img in images[:200]:  # max 200 per class per dataset
                    src = class_src / img
                    dst_name = f"{dataset_prefix}{img}"
                    dst = class_dst / dst_name
                    if not dst.exists():
                        shutil.copy2(src, dst)
                        copied += 1
                if copied > 0:
                    total_count = len(os.listdir(class_dst))
                    class_counts[dir_name] = class_counts.get(dir_name, 0) + copied
                    logger.info(f"  {dir_name}: +{copied} (total {class_counts[dir_name]})")

print(f"\n✅ Merged dataset ready: {MERGED_DIR}")
print(f"Total classes: {len(class_counts)}")
print("\nClass distribution:")
for cls in sorted(class_counts):
    print(f"{cls:30}: {class_counts[cls]} images")

total_images = sum(class_counts.values())
print(f"Total images: {total_images}")

print("\n📝 Next: Update notebook DATA_DIR = r'd:/PROJECT STAGE 1/dataset/merged_dataset'")
print("📋 Ready for training!")
