import os
import zipfile
import tarfile
from pathlib import Path

def unmask_and_extract():
    base_cache = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets")
    print(f"🕵️  UNMASKING ARCHIVES: {base_cache}")
    
    for root, dirs, files in os.walk(base_cache):
        for f in files:
            if f == "1.archive":
                fpath = Path(root) / f
                print(f"🔍 INSPECTING: {fpath}")
                
                # Try ZIP
                if zipfile.is_zipfile(fpath):
                    print(f"📦 FORMAT: ZIP. Extracting...")
                    with zipfile.ZipFile(fpath, 'r') as z:
                        z.extractall(root)
                    print("✅ SUCCESS")
                    continue
                
                # Try TAR
                try:
                    if tarfile.is_tarfile(fpath):
                        print(f"📦 FORMAT: TAR. Extracting...")
                        with tarfile.open(fpath, 'r') as t:
                            t.extractall(root)
                        print("✅ SUCCESS")
                        continue
                except: pass
                
                print("❌ FAILED: Unknown format")

if __name__ == "__main__":
    unmask_and_extract()
