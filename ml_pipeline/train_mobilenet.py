"""
Train MobileNetV2 Model for Medicinal Plant Classification
Uses transfer learning with ImageNet weights
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils import class_weight

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 1e-4

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "dataset" / "Indian Medicinal Leaves Image Datasets" / "Medicinal Leaf dataset"
OUTPUT_DIR = BASE_DIR / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("MEDICINAL PLANT CLASSIFICATION - MobileNetV2 Training")
print("=" * 70)
print(f"Data directory: {DATA_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Image size: {IMG_SIZE}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Epochs: {EPOCHS}")
print("=" * 70)


def create_data_generators():
    """Create train, validation, and test data generators"""
    print("\n📊 Creating data generators...")
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest',
        validation_split=0.2  # 80% train, 20% validation
    )
    
    # No augmentation for validation/test
    test_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )
    
    # Training generator
    train_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    # Validation generator
    val_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    num_classes = len(train_generator.class_indices)
    class_names = list(train_generator.class_indices.keys())
    
    print(f"✓ Found {num_classes} classes")
    print(f"✓ Training samples: {train_generator.samples}")
    print(f"✓ Validation samples: {val_generator.samples}")
    print(f"\nClasses: {', '.join(class_names[:5])}{'...' if len(class_names) > 5 else ''}")
    
    # Save class names
    class_names_path = OUTPUT_DIR / "class_names.json"
    with open(class_names_path, 'w') as f:
        json.dump(class_names, f, indent=2)
    print(f"✓ Saved class names to {class_names_path}")
    
    return train_generator, val_generator, num_classes, class_names


def create_model(num_classes):
    """Create MobileNetV2 model with transfer learning"""
    print("\n🏗️  Building MobileNetV2 model...")
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(*IMG_SIZE, 3),
        pooling='avg'
    )
    
    # Freeze base model layers initially
    base_model.trainable = False
    
    # Create model
    inputs = layers.Input(shape=(*IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = models.Model(inputs, outputs)
    
    # Compile model with Label Smoothing for better generalization
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
    )
    
    print(f"✓ Model created with {num_classes} output classes")
    print(f"✓ Total parameters: {model.count_params():,}")
    print(f"✓ Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    
    return model, base_model


def train_model(model, base_model, train_gen, val_gen):
    """Train the model"""
    print("\n🚀 Starting training...")
    
    # Callbacks
    checkpoint_path = OUTPUT_DIR / "mobilenetv2_best.h5"
    callbacks = [
        ModelCheckpoint(
            checkpoint_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Calculate class weights
    class_weights_list = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_gen.classes),
        y=train_gen.classes
    )
    class_weights_dict = dict(enumerate(class_weights_list))
    print(f"\n⚖️  Class weights calculated: {list(class_weights_dict.items())[:5]}...")

    # Phase 1: Train with frozen base
    print("\n📍 Phase 1: Training with frozen base model...")
    history1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=min(15, EPOCHS),
        callbacks=callbacks,
        class_weight=class_weights_dict,
        verbose=1
    )
    
    # Phase 2: Fine-tune with unfrozen base
    print("\n📍 Phase 2: Fine-tuning with unfrozen base model...")
    base_model.trainable = True
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
    )
    
    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        initial_epoch=len(history1.history['loss']),
        callbacks=callbacks,
        class_weight=class_weights_dict,
        verbose=1
    )
    
    # Combine histories
    history = {
        'loss': history1.history['loss'] + history2.history['loss'],
        'accuracy': history1.history['accuracy'] + history2.history['accuracy'],
        'val_loss': history1.history['val_loss'] + history2.history['val_loss'],
        'val_accuracy': history1.history['val_accuracy'] + history2.history['val_accuracy']
    }
    
    print(f"\n✓ Training completed!")
    print(f"✓ Best model saved to {checkpoint_path}")
    
    return history


def plot_training_history(history):
    """Plot training history"""
    print("\n📈 Plotting training history...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Accuracy plot
    ax1.plot(history['accuracy'], label='Train Accuracy')
    ax1.plot(history['val_accuracy'], label='Val Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Loss plot
    ax2.plot(history['loss'], label='Train Loss')
    ax2.plot(history['val_loss'], label='Val Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plot_path = OUTPUT_DIR / "training_history.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved training history plot to {plot_path}")
    plt.close()


def evaluate_model(model, val_gen, class_names):
    """Evaluate model and create confusion matrix"""
    print("\n📊 Evaluating model...")
    
    # Get predictions
    val_gen.reset()
    predictions = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(predictions, axis=1)
    y_true = val_gen.classes
    
    # Classification report
    print("\n" + "=" * 70)
    print("CLASSIFICATION REPORT")
    print("=" * 70)
    report = classification_report(y_true, y_pred, target_names=class_names)
    print(report)
    
    # Save report
    report_path = OUTPUT_DIR / "classification_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"✓ Saved classification report to {report_path}")
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    cm_path = OUTPUT_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved confusion matrix to {cm_path}")
    plt.close()
    
    # Calculate accuracy
    accuracy = np.sum(y_pred == y_true) / len(y_true)
    print(f"\n✓ Final Validation Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    return accuracy


def export_to_onnx(model):
    """Export model to ONNX format"""
    print("\n📦 Exporting model to ONNX format...")
    
    try:
        import tf2onnx
        
        onnx_path = OUTPUT_DIR / "mobilenetv2_best.onnx"
        
        # Convert to ONNX
        spec = (tf.TensorSpec((None, *IMG_SIZE, 3), tf.float32, name="input"),)
        model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec)
        
        with open(onnx_path, "wb") as f:
            f.write(model_proto.SerializeToString())
        
        print(f"✓ Exported model to {onnx_path}")
        
    except ImportError:
        print("⚠️  tf2onnx not installed. Skipping ONNX export.")
        print("   Install with: pip install tf2onnx")
    except Exception as e:
        print(f"⚠️  ONNX export failed: {e}")


def main():
    """Main training pipeline"""
    start_time = datetime.now()
    
    # Create data generators
    train_gen, val_gen, num_classes, class_names = create_data_generators()
    
    # Create model
    model, base_model = create_model(num_classes)
    
    # Train model
    history = train_model(model, base_model, train_gen, val_gen)
    
    # Plot history
    plot_training_history(history)
    
    # Evaluate model
    accuracy = evaluate_model(model, val_gen, class_names)
    
    # Export to ONNX
    export_to_onnx(model)
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"Duration: {duration}")
    print(f"Final Accuracy: {accuracy*100:.2f}%")
    print(f"Model saved to: {OUTPUT_DIR / 'mobilenetv2_best.h5'}")
    print(f"Class names saved to: {OUTPUT_DIR / 'class_names.json'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
