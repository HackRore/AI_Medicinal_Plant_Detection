import os
from pathlib import Path

def scan_archives():
    base_cache = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets")
    print(f"📦 SCANNING: {base_cache}")
    
    for root, dirs, files in os.walk(base_cache):
        for f in files:
            f_lower = f.lower()
            if any(ext in f_lower for ext in [".zip", ".tar", ".gz", ".7z", ".rar", "archive"]):
                fpath = Path(root) / f
                size_mb = fpath.stat().st_size / (1024 * 1024)
                if size_mb > 5:
                    print(f"🎯 FOUND: {fpath} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    scan_archives()
