import kagglehub
import os
from pathlib import Path

def reacquire():
    datasets = [
        'mdfahimbinalam/leaf-dataset',
        'rayush/plant-leaves',
        'hmohamedhussain/leaves-image-dataset'
    ]
    
    for ds in datasets:
        print(f"🚀 REDOWNLOADING/EXTRACTING: {ds}...")
        try:
            # force_download=True should re-trigger the extraction logic in kagglehub
            path = kagglehub.dataset_download(ds)
            print(f"✅ PATH: {path}")
            
            # Check if extracted (look for directories)
            subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
            print(f"📁 SUBDIRS FOUND: {len(subdirs)}")
            if len(subdirs) < 2:
                print(f"⚠️  WARNING: Dataset might still be compressed at {path}")
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    reacquire()
