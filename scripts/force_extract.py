import os
import zipfile
from pathlib import Path

def force_extract():
    targets = [
        r"C:\Users\HackRore\.cache\kagglehub\datasets\rayush\plant-leaves\data.zip",
        r"C:\Users\HackRore\.cache\kagglehub\datasets\rizkikecek\dataset-herbal-leaves\data.zip"
    ]
    
    for t in targets:
        p = Path(t)
        if not p.exists():
            print(f"❌ NOT FOUND: {t}")
            continue
            
        print(f"🔓 EXTRACTING: {t} -> {p.parent}")
        try:
            with zipfile.ZipFile(p, 'r') as z:
                z.extractall(p.parent)
            print(f"✅ SUCCESS")
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    force_extract()
