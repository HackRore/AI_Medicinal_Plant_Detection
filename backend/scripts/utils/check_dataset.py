import os
from pathlib import Path

DATA_DIR = Path(r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset")

def count_images():
    if not DATA_DIR.exists():
        print(f"Directory not found: {DATA_DIR}")
        return

    print(f"Scanning {DATA_DIR}...")
    class_counts = {}
    total_images = 0
    
    for class_dir in DATA_DIR.iterdir():
        if class_dir.is_dir():
            count = len(list(class_dir.glob("*.jpg"))) + len(list(class_dir.glob("*.jpeg"))) + len(list(class_dir.glob("*.png")))
            class_counts[class_dir.name] = count
            total_images += count
            
    # Sort by count
    sorted_counts = sorted(class_counts.items(), key=lambda x: x[1])
    
    print("\n--- Image Counts per Class ---")
    for name, count in sorted_counts:
        print(f"{name}: {count}")
        
    print(f"\nTotal Classes: {len(class_counts)}")
    print(f"Total Images: {total_images}")
    if len(class_counts) > 0:
        print(f"Average Images per Class: {total_images / len(class_counts):.1f}")
        print(f"Min: {sorted_counts[0]}")
        print(f"Max: {sorted_counts[-1]}")

if __name__ == "__main__":
    count_images()
