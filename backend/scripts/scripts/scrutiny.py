import os
from pathlib import Path

def scrutiny():
    base_cache = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets")
    print(f"🔎 DEEP SCRUTINY: {base_cache}")
    
    for root, dirs, files in os.walk(base_cache):
        for f in files:
            fpath = Path(root) / f
            size_mb = fpath.stat().st_size / (1024 * 1024)
            if size_mb > 10:
                print(f"📄 FILE: {fpath} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    scrutiny()
