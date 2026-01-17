"""
Enhanced Medicinal Plant Classification Training
Uses EfficientNetV2-S with advanced augmentation and fine-tuning
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks, optimizers
from tensorflow.keras.applications import EfficientNetV2S
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils import class_weight
import matplotlib.pyplot as plt

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 16  # Smaller batch size for EfficientNetV2-S
EPOCHS = 30
LEARNING_RATE = 1e-4

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "dataset" / "Indian Medicinal Leaves Image Datasets" / "Medicinal Leaf dataset"
OUTPUT_DIR = BASE_DIR / "models" / "enhanced"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def build_enhanced_model(num_classes):
    """Build EfficientNetV2-S based model"""
    base_model = EfficientNetV2S(
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
        include_top=False,
        weights='imagenet',
        include_preprocessing=True # Internal rescaling
    )
    
    # Freeze base model initially
    base_model.trainable = False
    
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.4),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
    )
    
    return model, base_model

def train():
    print("🚀 Starting Enhanced Training Pipeline...")
    
    # Advanced Data Augmentation
    train_datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest',
        validation_split=0.2
    )
    
    train_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    
    val_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    num_classes = len(train_generator.class_indices)
    
    # Save class names for inference mapping
    with open(OUTPUT_DIR / "class_names.json", "w") as f:
        json.dump(train_generator.class_indices, f)
    
    # Compute class weights for imbalance
    weights = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_generator.classes),
        y=train_generator.classes
    )
    class_weights_dict = dict(enumerate(weights))
    
    model, base_model = build_enhanced_model(num_classes)
    
    # Callbacks
    checkpoint = callbacks.ModelCheckpoint(
        OUTPUT_DIR / "efficientnetv2_best.h5",
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )
    
    early_stop = callbacks.EarlyStopping(
        monitor='val_loss',
        patience=8,
        restore_best_weights=True
    )
    
    # Phase 1: Training top layers
    print("\nPhase 1: Training top layers...")
    model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=10,
        class_weight=class_weights_dict,
        callbacks=[checkpoint, early_stop]
    )
    
    # Phase 2: Fine-tuning the whole model
    print("\nPhase 2: Fine-tuning with lower learning rate...")
    base_model.trainable = True
    model.compile(
        optimizer=optimizers.Adam(learning_rate=LEARNING_RATE / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
    )
    
    model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        class_weight=class_weights_dict,
        callbacks=[checkpoint, early_stop]
    )
    
    print("\n✅ Training Complete. Best model saved to enhanced/efficientnetv2_best.h5")

if __name__ == "__main__":
    train()
