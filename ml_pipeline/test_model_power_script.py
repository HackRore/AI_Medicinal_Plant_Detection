"""
AI Model Power Test - Automated Script
Group G9 - Medicinal Plant Detection System
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image

print("=" * 80)
print("🧠 AI MODEL POWER TEST - GROUP G9")
print("=" * 80)

# Configuration
IMG_SIZE = (224, 224)
MODEL_PATH = Path("models/mobilenetv2_best.h5")
CLASS_NAMES_PATH = Path("models/class_names.json")
DATASET_PATH = Path("../dataset/Indian Medicinal Leaves Image Datasets/Medicinal Leaf dataset")

# Check if model exists
if not MODEL_PATH.exists():
    print("\n❌ MODEL NOT FOUND")
    print(f"   Expected location: {MODEL_PATH.absolute()}")
    print("\n📋 Model Status:")
    print("   - The model needs to be trained first")
    print("   - Run: python train_mobilenet.py")
    print("   - Or use the existing trained model if available")
    print("\n💡 What this test would do:")
    print("   ✓ Load the MobileNetV2 model")
    print("   ✓ Test on 5 medicinal plant images (Tulsi, Aloevera, Neem, Mint, Betel)")
    print("   ✓ Show predictions with confidence scores")
    print("   ✓ Calculate accuracy metrics")
    print("   ✓ Generate visualization charts")
    print("\n🎯 Current System Status:")
    
    # Check dataset
    if DATASET_PATH.exists():
        classes = [d.name for d in DATASET_PATH.iterdir() if d.is_dir()]
        print(f"   ✅ Dataset found: {len(classes)} plant classes")
        print(f"   📂 Location: {DATASET_PATH.absolute()}")
        print(f"\n   Sample classes:")
        for cls in classes[:10]:
            print(f"      - {cls}")
    else:
        print(f"   ❌ Dataset not found at: {DATASET_PATH.absolute()}")
    
    # Check class names
    if CLASS_NAMES_PATH.exists():
        with open(CLASS_NAMES_PATH, 'r') as f:
            class_names = json.load(f)
        print(f"\n   ✅ Class names file found: {len(class_names)} classes")
    else:
        print(f"\n   ❌ Class names file not found")
    
    print("\n" + "=" * 80)
    print("📝 NEXT STEPS:")
    print("=" * 80)
    print("1. Train the model:")
    print("   cd ml_pipeline")
    print("   python train_mobilenet.py")
    print("\n2. Or copy existing model to:")
    print(f"   {MODEL_PATH.absolute()}")
    print("\n3. Then run this test again:")
    print("   python test_model_power_script.py")
    print("=" * 80)
    
else:
    print("\n✅ MODEL FOUND - Starting comprehensive testing...")
    
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model
        from tensorflow.keras.preprocessing import image
        
        print(f"\n📊 TensorFlow Version: {tf.__version__}")
        print(f"🖥️  GPU Available: {len(tf.config.list_physical_devices('GPU')) > 0}")
        
        # Load model
        print(f"\n🔄 Loading model from {MODEL_PATH}...")
        model = load_model(MODEL_PATH)
        print("✅ Model loaded successfully!")
        
        # Load class names
        with open(CLASS_NAMES_PATH, 'r') as f:
            class_data = json.load(f)
            # Handle both list and dict formats
            if isinstance(class_data, list):
                class_names = {i: name for i, name in enumerate(class_data)}
            else:
                class_names = {v: k for k, v in class_data.items()}
        
        print(f"\n📚 Total Classes: {len(class_names)}")
        
        # Define prediction function
        def preprocess_image(img_path, target_size=(224, 224)):
            img = image.load_img(img_path, target_size=target_size)
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0
            return img_array
        
        def predict_plant(img_path, model, class_names, top_k=5):
            img_array = preprocess_image(img_path)
            predictions = model.predict(img_array, verbose=0)[0]
            top_indices = np.argsort(predictions)[::-1][:top_k]
            return [(class_names[idx], float(predictions[idx])) for idx in top_indices]
        
        # Select test images
        test_classes = ['Tulsi', 'Aloevera', 'Neem', 'Mint', 'Betel']
        test_images = []
        
        for class_name in test_classes:
            class_dir = DATASET_PATH / class_name
            if class_dir.exists():
                images = list(class_dir.glob('*.jpg'))[:1]
                if images:
                    test_images.append({'path': images[0], 'true_class': class_name})
        
        print(f"\n📸 Testing on {len(test_images)} images...")
        print("=" * 80)
        
        # Run predictions
        correct = 0
        for idx, test_img in enumerate(test_images, 1):
            predictions = predict_plant(test_img['path'], model, class_names, top_k=3)
            predicted_class, confidence = predictions[0]
            is_correct = predicted_class == test_img['true_class']
            
            if is_correct:
                correct += 1
            
            status = "✅ CORRECT" if is_correct else "❌ WRONG"
            print(f"\n{status} - Test {idx}/{len(test_images)}")
            print(f"  True Class:  {test_img['true_class']}")
            print(f"  Predicted:   {predicted_class}")
            print(f"  Confidence:  {confidence*100:.2f}%")
            print(f"  Top 3:")
            for i, (cls, conf) in enumerate(predictions, 1):
                print(f"    {i}. {cls}: {conf*100:.2f}%")
            print("-" * 80)
        
        accuracy = (correct / len(test_images)) * 100 if test_images else 0
        print(f"\n🏆 OVERALL ACCURACY: {accuracy:.2f}% ({correct}/{len(test_images)})")
        print("=" * 80)
        
        print("\n✅ Test completed successfully!")
        print("📊 For visual charts, run the Jupyter notebook: test_model_power.ipynb")
        
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\n💡 Install TensorFlow:")
        print("   python -m pip install tensorflow")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

print("\n" + "=" * 80)
print("Developed by Group G9 | Dr. DY Patil College of Eng. and Innovation")
print("=" * 80)
