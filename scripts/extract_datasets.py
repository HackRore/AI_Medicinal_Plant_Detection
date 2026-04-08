import os
import zipfile
from pathlib import Path

def extract_archives():
    base_cache = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets")
    print(f"📦 SCANNING FOR ARCHIVES: {base_cache}")
    
    for root, dirs, files in os.walk(base_cache):
        for f in files:
            if f.endswith('.zip'):
                fpath = Path(root) / f
                print(f"🔓 EXTRACTING: {fpath}")
                try:
                    with zipfile.ZipFile(fpath, 'r') as zip_ref:
                        zip_ref.extractall(root)
                    print(f"✅ SUCCESS")
                except Exception as e:
                    print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    extract_archives()
