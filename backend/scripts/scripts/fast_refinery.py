import os
import shutil
from pathlib import Path

# Config
RAW_DIR = Path(r"d:\PROJECT STAGE 1\dataset\raw")
UNIFIED_DIR = Path(r"d:\PROJECT STAGE 1\dataset\unified")

def refinery():
    if UNIFIED_DIR.exists():
        shutil.rmtree(UNIFIED_DIR)
    UNIFIED_DIR.mkdir(parents=True)
    
    print(f"Refining data from {RAW_DIR}...")
    for ds_dir in RAW_DIR.iterdir():
        if not ds_dir.is_dir(): continue
        
        # Handle leaf-dataset/Dataset structure
        src_root = ds_dir
        if (ds_dir / "Dataset").exists():
            src_root = ds_dir / "Dataset"
            
        for species_dir in src_root.iterdir():
            if not species_dir.is_dir(): continue
            
            clean_name = species_dir.name.lower().replace("_", " ").title()
            target_path = UNIFIED_DIR / clean_name
            target_path.mkdir(exist_ok=True)
            
            # Copy first 200 images for ultra-fast training
            files = list(species_dir.glob("*"))[:200]
            for f in files:
                shutil.copy(f, target_path / f.name)
                
    print(f"Refinery complete. Unified dataset at {UNIFIED_DIR}")

if __name__ == "__main__":
    refinery()
