"""
Train a binary Leaf Gate model (leaf vs non-leaf).

Goal (project intent):
- If image is NOT a plant leaf -> reject early ("Not a Plant Leaf")
- If it IS a leaf -> allow species classifier to run

Dataset layout (recommended):
dataset/
  leaf_gate/
    train/
      leaf/
      non_leaf/
    val/
      leaf/
      non_leaf/
    test/
      leaf/
      non_leaf/

Notes:
- Use many diverse NON-LEAF negatives (hands, faces, cars, soil, sky, flowers, stems, random objects).
- The key metric is LOW false-accept rate for non-leaf while keeping high recall for leaf.
"""

import json
from pathlib import Path
from datetime import datetime

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from sklearn.metrics import classification_report, confusion_matrix


IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 3
LEARNING_RATE = 1e-4

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "dataset" / "leaf_gate"
OUTPUT_DIR = BASE_DIR / "models" / "leaf_gate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_generators():
    train_dir = DATA_DIR / "train"
    val_dir = DATA_DIR / "val"

    train_aug = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=25,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        brightness_range=(0.8, 1.2),
        fill_mode="nearest",
    )

    val_aug = ImageDataGenerator(rescale=1.0 / 255.0)

    class_order = ["non_leaf", "leaf"]

    train_gen = train_aug.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        classes=class_order,
        shuffle=True,
    )

    val_gen = val_aug.flow_from_directory(
        val_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        classes=class_order,
        shuffle=False,
    )

    # Convention required by runtime:
    # index 1 = leaf, index 0 = non_leaf
    class_indices = train_gen.class_indices
    if class_indices.get("non_leaf") != 0 or class_indices.get("leaf") != 1:
        raise RuntimeError(f"Class index convention mismatch. Got {class_indices}")

    with open(OUTPUT_DIR / "class_names.json", "w") as f:
        json.dump(["non_leaf", "leaf"], f, indent=2)

    return train_gen, val_gen


def build_model():
    base = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(*IMG_SIZE, 3),
        pooling="avg",
    )
    base.trainable = False

    inputs = layers.Input(shape=(*IMG_SIZE, 3))
    x = base(inputs, training=False)
    x = layers.Dropout(0.25)(x)
    x = layers.Dense(128, activation="relu")(x)
    outputs = layers.Dense(2, activation="softmax")(x)
    model = models.Model(inputs, outputs)

    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.05),
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model, base


def train(model, base, train_gen, val_gen):
    best_path = OUTPUT_DIR / "leaf_gate_best.h5"
    callbacks = [
        ModelCheckpoint(best_path, monitor="val_auc", save_best_only=True, mode="max", verbose=1),
        EarlyStopping(monitor="val_auc", patience=6, mode="max", restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_auc", factor=0.5, patience=3, mode="max", min_lr=1e-7, verbose=1),
    ]

    # Phase 1
    model.fit(train_gen, validation_data=val_gen, epochs=min(8, EPOCHS), callbacks=callbacks, verbose=1)

    # Phase 2 fine-tune
    base.trainable = True
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE / 10),
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS, callbacks=callbacks, verbose=1)

    return best_path


def evaluate(model, val_gen):
    val_gen.reset()
    probs = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(probs, axis=1)
    y_true = val_gen.classes

    report = classification_report(y_true, y_pred, target_names=["non_leaf", "leaf"])
    with open(OUTPUT_DIR / "val_classification_report.txt", "w") as f:
        f.write(report)

    cm = confusion_matrix(y_true, y_pred)
    with open(OUTPUT_DIR / "val_confusion_matrix.json", "w") as f:
        json.dump(cm.tolist(), f, indent=2)

    print(report)
    print("Confusion matrix:")
    print(cm)


def export_onnx(keras_model_path: Path):
    try:
        import tf2onnx
    except Exception as e:
        print(f"tf2onnx not available: {e}")
        print("Install with: python -m pip install tf2onnx")
        return

    model = tf.keras.models.load_model(keras_model_path, compile=False)
    spec = (tf.TensorSpec((None, *IMG_SIZE, 3), tf.float32, name="input"),)
    model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13)

    out_path = OUTPUT_DIR / "leaf_gate.onnx"
    out_path.write_bytes(model_proto.SerializeToString())
    print(f"Exported ONNX to {out_path}")
    print("\nCopy this file to backend:")
    print(f"  {out_path}  ->  backend/ml_models/leaf_gate.onnx")


def main():
    print("=" * 80)
    print("LEAF GATE TRAINING (leaf vs non-leaf)")
    print("=" * 80)
    print(f"Data:   {DATA_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Start:  {datetime.now().isoformat(timespec='seconds')}")

    train_gen, val_gen = make_generators()
    model, base = build_model()
    best_path = train(model, base, train_gen, val_gen)

    # Reload best for eval/export
    best_model = tf.keras.models.load_model(best_path, compile=False)
    best_model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    evaluate(best_model, val_gen)
    export_onnx(best_path)

    print(f"Done: {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()

