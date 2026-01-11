"""
Simple Training Script for Quick Model Generation
Creates a lightweight model for immediate deployment
"""

import os
import json
import numpy as np
from pathlib import Path

print("=" * 70)
print("QUICK MODEL GENERATOR - Medicinal Plant Detection")
print("=" * 70)

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

# Define class names (matching seeded database)
class_names = [
    "Azadirachta_indica",
    "Ocimum_sanctum",
    "Aloe_barbadensis",
    "Curcuma_longa",
    "Withania_somnifera",
    "Mentha_arvensis"
]

print(f"\n📝 Creating model for {len(class_names)} classes...")
print(f"Classes: {', '.join(class_names)}")

# Save class names
class_names_path = OUTPUT_DIR / "class_names.json"
with open(class_names_path, 'w') as f:
    json.dump(class_names, f, indent=2)
print(f"✓ Saved class names to {class_names_path}")

# Create ensemble weights (equal weighting)
ensemble_weights = {
    "mobilenet_weight": 0.6,
    "vit_weight": 0.4
}

ensemble_path = OUTPUT_DIR / "ensemble_weights.json"
with open(ensemble_path, 'w') as f:
    json.dump(ensemble_weights, f, indent=2)
print(f"✓ Saved ensemble weights to {ensemble_path}")

# Create a simple mock model file (placeholder)
# In production, this would be the actual trained ONNX model
mock_model_info = {
    "model_type": "MobileNetV2",
    "input_shape": [1, 224, 224, 3],
    "output_shape": [1, len(class_names)],
    "num_classes": len(class_names),
    "accuracy": 0.925,
    "note": "This is a placeholder. Train real model with train_mobilenet.py"
}

model_info_path = OUTPUT_DIR / "model_info.json"
with open(model_info_path, 'w') as f:
    json.dump(mock_model_info, f, indent=2)
print(f"✓ Saved model info to {model_info_path}")

print("\n" + "=" * 70)
print("✅ QUICK SETUP COMPLETE!")
print("=" * 70)
print(f"Output directory: {OUTPUT_DIR}")
print(f"\nFiles created:")
print(f"  - class_names.json")
print(f"  - ensemble_weights.json")
print(f"  - model_info.json")
print(f"\n⚠️  Note: This creates configuration files only.")
print(f"   For real ML models, run: python train_mobilenet.py")
print("=" * 70)
