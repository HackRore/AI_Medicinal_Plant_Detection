"""
Test a trained Leaf Gate model on the test split and report metrics.

Usage:
  cd ml_pipeline
  python test_leaf_gate.py

Expects:
  ml_pipeline/models/leaf_gate/leaf_gate_best.h5
  dataset/leaf_gate/test/{leaf,non_leaf}
"""

import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


IMG_SIZE = (224, 224)
BATCH_SIZE = 32

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "dataset" / "leaf_gate"
MODEL_DIR = BASE_DIR / "models" / "leaf_gate"
MODEL_PATH = MODEL_DIR / "leaf_gate_best.h5"


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run train_leaf_gate.py first.")

    test_dir = DATA_DIR / "test"
    if not test_dir.exists():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    gen = ImageDataGenerator(rescale=1.0 / 255.0).flow_from_directory(
        test_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        classes=["non_leaf", "leaf"],
        shuffle=False,
    )

    # Must match training convention
    if set(gen.class_indices.keys()) != {"non_leaf", "leaf"}:
        raise RuntimeError(f"Expected classes {{'non_leaf','leaf'}}, got {set(gen.class_indices.keys())}")

    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    probs = model.predict(gen, verbose=1)

    y_true = gen.classes
    y_pred = np.argmax(probs, axis=1)
    leaf_prob = probs[:, 1]

    report = classification_report(y_true, y_pred, target_names=["non_leaf", "leaf"])
    cm = confusion_matrix(y_true, y_pred)
    auc = roc_auc_score(y_true, leaf_prob)

    print(report)
    print("Confusion matrix:")
    print(cm)
    print(f"AUC: {auc:.4f}")

    out = {
        "class_indices": gen.class_indices,
        "confusion_matrix": cm.tolist(),
        "auc": float(auc),
    }
    (MODEL_DIR / "test_metrics.json").write_text(json.dumps(out, indent=2))
    print(f"Saved: {MODEL_DIR / 'test_metrics.json'}")


if __name__ == "__main__":
    main()

