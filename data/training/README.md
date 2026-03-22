# Training Data Directory Structure

This folder contains medicinal plant leaf images for training the hybrid EfficientNet + Swin Transformer model.

## Folder Organization

```
/data/training/
├── Neem/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   ├── img_003.jpg
│   └── ...
├── Tulsi/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ...
├── Turmeric/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ...
├── Mint/
├── Aloe/
├── Ashwagandha/
└── ... (other plant species)
```

## Requirements

1. **Folder Names**: Must match plant species names (case-sensitive)
   - Examples: `Neem`, `Tulsi`, `Turmeric`, `Mint`, `Aloe`, `Ashwagandha`
   - No spaces in folder names (use underscores if needed: `Indian_Ginseng`)

2. **Image Format**: JPG or PNG
   - Minimum resolution: 224x224 pixels
   - Recommended: 512x512 or higher for better accuracy
   - File size: 50KB - 5MB per image

3. **Image Content**:
   - Clear leaf close-ups
   - Well-lit, minimal shadows
   - Single leaf or small cluster
   - Plain background preferred
   - No duplicate images

4. **Minimum Images per Class**:
   - For initial training: 20-50 images per species (minimum)
   - For production quality: 100+ images per species
   - Balanced dataset: Similar number of images across species

5. **Data Quality**:
   - All images should pass quality gate checks:
     - Blur score > 100 (Laplacian variance)
     - Brightness: 30-225 range
     - Object size: 15-90% of frame

## Naming Conventions

- File names: `img_001.jpg`, `sample_neem_005.png`
- Use descriptive names if possible: `neem_leaf_clear_lighting.jpg`
- Avoid special characters except hyphens/underscores

## Example Folder Creation

```bash
mkdir -p data/training/Neem
mkdir -p data/training/Tulsi
mkdir -p data/training/Turmeric
mkdir -p data/training/Mint
mkdir -p data/training/Aloe
mkdir -p data/training/Ashwagandha
mkdir -p data/training/Ginger
mkdir -p data/training/Basil
mkdir -p data/training/Lemon_Grass
```

## Training Script Usage

Once data is organized, run:

```bash
cd ml_pipeline
python train_hybrid_model.py \
  --data-dir ../data/training \
  --epochs 100 \
  --batch-size 32 \
  --model efficientnet-swin \
  --output-dir ./models
```

## Data Augmentation

The training pipeline will automatically apply:
- Random rotation (±15°)
- Horizontal flip (50% probability)
- Brightness/contrast adjustment
- Zoom (10-110%)
- Gaussian blur (controlled)

So you don't need to create augmented versions manually.

## Validation & Test Split

- Training: 70% of images
- Validation: 15% of images
- Test: 15% of images

(Automatically split by training script)

## Quality Assurance Checklist

Before training:
- [ ] All files are valid JPEG/PNG
- [ ] No corrupted images
- [ ] Image sizes are consistent and reasonable
- [ ] At least 20 images per species
- [ ] Folder names match expected plant species
- [ ] No empty folders
- [ ] All text is readable in image metadata

## Handling Imbalanced Datasets

If you have unequal images per class:

```bash
python ml_pipeline/balance_dataset.py \
  --data-dir data/training \
  --method oversample  # or 'undersample'
```

This will balance classes using over/undersampling.

## Adding New Plant Species

1. Create new folder: `data/training/YourPlant/`
2. Add at least 20 images
3. Re-train model (will automatically detect new class)

## Updating with Quality-Checked Images

To only include images that pass quality checks:

```bash
python ml_pipeline/quality_filter_dataset.py \
  --data-dir data/training \
  --strict  # Use strict thresholds
  --output-dir data/training_filtered
```

This will copy only high-quality images to `data/training_filtered/`.

---

**Ready to train? Run:** `python ml_pipeline/train_hybrid_model.py`
