import zipfile
import os
from pathlib import Path

src = r"C:\Users\HackRore\.cache\kagglehub\datasets\rizkikecek\dataset-herbal-leaves\1.zip"
dest = r"D:\PROJECT STAGE 1\dataset\raw\rizkikecek"

def extract():
    print(f"Extracting {src} to {dest}...")
    Path(dest).mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(src, 'r') as zip_ref:
            zip_ref.extractall(dest)
        print("Extraction complete.")
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    extract()
