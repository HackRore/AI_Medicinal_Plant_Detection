import zipfile
from pathlib import Path

def extract_v2():
    p1 = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets\rizkikecek\dataset-herbal-leaves\1.archive")
    p2 = Path(r"C:\Users\HackRore\.cache\kagglehub\datasets\rayush\plant-leaves\1.archive")
    
    for p in [p1, p2]:
        if p.exists():
            print(f"🔓 EXTRACTING: {p} -> {p.parent}")
            try:
                with zipfile.ZipFile(p, 'r') as z:
                    z.extractall(p.parent)
                print("✅ SUCCESS")
            except Exception as e:
                print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    extract_v2()
