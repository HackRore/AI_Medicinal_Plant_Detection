import kagglehub
import os
import shutil
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
BASE_DIR = r"d:\PROJECT STAGE 1"
RAW_DIR = os.path.join(BASE_DIR, "dataset", "raw")
UNIFIED_DIR = os.path.join(BASE_DIR, "dataset", "unified")

DATASETS = [
    "mdfahimbinalam/leaf-dataset",          # 145MB
    "mahirdipto/plant-leaf-test",           # ~50MB
    "hmohamedhussain/leaves-image-dataset", # ~100MB
    "abdallahalidev/plantvillage-dataset",  # ~800MB
    "rayush/plant-leaves"                   # 4.55GB (Move to end)
]

def ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(UNIFIED_DIR, exist_ok=True)

def download_all():
    logger.info("Starting Multi-Dataset Acquisition (Robust Mode)...")
    for ds_name in DATASETS:
        folder_name = ds_name.split("/")[-1]
        dest_dir = os.path.join(RAW_DIR, folder_name)
        
        if os.path.exists(dest_dir) and len(os.listdir(dest_dir)) > 0:
            logger.info(f"Dataset {ds_name} already exists. Skipping mirroring.")
            continue

        retries = 3
        while retries > 0:
            try:
                logger.info(f"Downloading {ds_name} (Retries left: {retries})...")
                path = kagglehub.dataset_download(ds_name)
                logger.info(f"Downloaded to: {path}")
                
                if os.path.exists(dest_dir):
                    shutil.rmtree(dest_dir)
                
                shutil.copytree(path, dest_dir)
                logger.info(f"Mirrored {ds_name} to local {dest_dir}")
                break
            except Exception as e:
                retries -= 1
                logger.error(f"Error downloading {ds_name}: {e}")
                if retries > 0:
                    time.sleep(10)
                else:
                    logger.critical(f"Aborting download for {ds_name} after multiple failures.")

if __name__ == "__main__":
    ensure_dirs()
    download_all()
