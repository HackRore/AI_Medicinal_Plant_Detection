"""
Build dataset/leaf_gate splits from existing repo datasets.

Leaf positives:
  dataset/Indian Medicinal Leaves Image Datasets/Medicinal Leaf dataset/**/*

Non-leaf negatives (hard negatives):
  dataset/Indian Medicinal Leaves Image Datasets/Medicinal plant dataset/**/*

Creates:
  dataset/leaf_gate/{train,val,test}/{leaf,non_leaf}
"""

from __future__ import annotations

import random
import shutil
from pathlib import Path


SEED = 42
TRAIN_FRAC = 0.8
VAL_FRAC = 0.1
TEST_FRAC = 0.1
MAX_PER_CLASS: int | None = 2000  # cap size for faster training on CPU


def iter_images(root: Path):
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def main():
    repo = Path(__file__).resolve().parents[1]

    leaf_root = repo / "dataset" / "Indian Medicinal Leaves Image Datasets" / "Medicinal Leaf dataset"
    non_leaf_root = repo / "dataset" / "Indian Medicinal Leaves Image Datasets" / "Medicinal plant dataset"
    out_root = repo / "dataset" / "leaf_gate"

    if not leaf_root.exists():
        raise FileNotFoundError(f"Leaf dataset not found: {leaf_root}")
    if not non_leaf_root.exists():
        raise FileNotFoundError(f"Plant dataset not found: {non_leaf_root}")

    leaf_imgs = list(iter_images(leaf_root))
    non_leaf_imgs = list(iter_images(non_leaf_root))
    if not leaf_imgs or not non_leaf_imgs:
        raise RuntimeError("No images found for leaf/non_leaf sources.")

    random.seed(SEED)
    random.shuffle(leaf_imgs)
    random.shuffle(non_leaf_imgs)

    n = min(len(leaf_imgs), len(non_leaf_imgs))
    if MAX_PER_CLASS is not None:
        n = min(n, int(MAX_PER_CLASS))

    leaf_imgs = leaf_imgs[:n]
    non_leaf_imgs = non_leaf_imgs[:n]

    def split(arr):
        n_total = len(arr)
        n_train = int(n_total * TRAIN_FRAC)
        n_val = int(n_total * VAL_FRAC)
        train = arr[:n_train]
        val = arr[n_train : n_train + n_val]
        test = arr[n_train + n_val :]
        return train, val, test

    leaf_split = split(leaf_imgs)
    non_leaf_split = split(non_leaf_imgs)

    # Create folders
    for split_name in ["train", "val", "test"]:
        for cls in ["leaf", "non_leaf"]:
            (out_root / split_name / cls).mkdir(parents=True, exist_ok=True)

    # Clear existing contents (only within leaf_gate)
    for split_name in ["train", "val", "test"]:
        for cls in ["leaf", "non_leaf"]:
            target = out_root / split_name / cls
            for f in target.iterdir():
                if f.is_file():
                    f.unlink()

    def copy_many(paths, target_dir: Path, prefix: str):
        for i, src in enumerate(paths):
            dst = target_dir / f"{prefix}_{i:06d}{src.suffix.lower()}"
            shutil.copy2(src, dst)

    for split_name, leaf_part, non_leaf_part in zip(
        ["train", "val", "test"], leaf_split, non_leaf_split
    ):
        copy_many(leaf_part, out_root / split_name / "leaf", "leaf")
        copy_many(non_leaf_part, out_root / split_name / "non_leaf", "non_leaf")

    print("Built dataset/leaf_gate")
    print(f"Leaf images per split: train={len(leaf_split[0])} val={len(leaf_split[1])} test={len(leaf_split[2])}")
    print(f"Non-leaf images per split: train={len(non_leaf_split[0])} val={len(non_leaf_split[1])} test={len(non_leaf_split[2])}")
    print(f"Output: {out_root}")


if __name__ == "__main__":
    main()

