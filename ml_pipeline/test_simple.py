"""
AI Model Power Test - Simple Version
Group G9 - Medicinal Plant Detection System
"""

import os
import json
import numpy as np
from pathlib import Path

print("=" * 80)
print("AI MODEL POWER TEST - GROUP G9")
print("=" * 80)

# Configuration
MODEL_PATH = Path("models/mobilenetv2_best.h5")
CLASS_NAMES_PATH = Path("models/class_names.json")
DATASET_PATH = Path("../dataset/Indian Medicinal Leaves Image Datasets/Medicinal Leaf dataset")

if not MODEL_PATH.exists():
    print("\nMODEL NOT FOUND")
    print(f"Expected: {MODEL_PATH.absolute()}")
    print("\nPlease train the model first:")
    print("  python train_mobilenet.py")
else:
    print("\nMODEL FOUND - Starting tests...")
    
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model
        from tensorflow.keras.preprocessing import image
        
        print(f"\nTensorFlow Version: {tf.__version__}")
        print(f"GPU Available: {len(tf.config.list_physical_devices('GPU')) > 0}")
        
        # Load model
        print(f"\nLoading model...")
        model = load_model(MODEL_PATH)
        print("Model loaded successfully!")
        
        # Load class names
        with open(CLASS_NAMES_PATH, 'r') as f:
            class_data = json.load(f)
            if isinstance(class_data, list):
                class_names = {i: name for i, name in enumerate(class_data)}
            else:
                class_names = {v: k for k, v in class_data.items()}
        
        print(f"\nTotal Classes: {len(class_names)}")
        print(f"Classes: {list(class_names.values())[:5]}...")
        
        # Prediction function
        def predict_plant(img_path):
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0
            predictions = model.predict(img_array, verbose=0)[0]
            top_idx = np.argmax(predictions)
            return class_names[top_idx], float(predictions[top_idx])
        
        # Test on sample images
        test_classes = ['Tulsi', 'Aloevera', 'Neem', 'Mint', 'Betel']
        test_images = []
        
        for class_name in test_classes:
            class_dir = DATASET_PATH / class_name
            if class_dir.exists():
                images = list(class_dir.glob('*.jpg'))[:1]
                if images:
                    test_images.append({'path': images[0], 'true_class': class_name})
        
        if not test_images:
            print("\nNo test images found in dataset")
            print(f"Dataset path: {DATASET_PATH.absolute()}")
        else:
            print(f"\nTesting on {len(test_images)} images...")
            print("=" * 80)
            
            correct = 0
            for idx, test_img in enumerate(test_images, 1):
                predicted_class, confidence = predict_plant(test_img['path'])
                is_correct = predicted_class == test_img['true_class']
                
                if is_correct:
                    correct += 1
                
                status = "CORRECT" if is_correct else "WRONG"
                print(f"\n[{status}] Test {idx}/{len(test_images)}")
                print(f"  True:       {test_img['true_class']}")
                print(f"  Predicted:  {predicted_class}")
                print(f"  Confidence: {confidence*100:.2f}%")
                print("-" * 80)
            
            accuracy = (correct / len(test_images)) * 100
            print(f"\nOVERALL ACCURACY: {accuracy:.2f}% ({correct}/{len(test_images)})")
            print("=" * 80)
        
        print("\nTest completed successfully!")
        
    except ImportError as e:
        print(f"\nMissing dependency: {e}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

print("\nDeveloped by Group G9")
print("Dr. DY Patil College of Eng. and Innovation")
print("=" * 80)
