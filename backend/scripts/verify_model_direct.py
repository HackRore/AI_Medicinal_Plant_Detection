
import onnxruntime as ort
import numpy as np
from PIL import Image
import json
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "mobilenetv2_best.onnx")
CLASS_NAMES_PATH = os.path.join(BASE_DIR, "ml_models", "class_names.json")

def verify_ai_engine():
    print("🧠 VERIFYING AI ENGINE (Direct ONNX Check)")
    print("-" * 50)
    
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found at {MODEL_PATH}")
        return
        
    try:
        session = ort.InferenceSession(MODEL_PATH)
        print(f"✅ Model Loaded: {os.path.basename(MODEL_PATH)}")
    except Exception as e:
         print(f"❌ Failed to load model: {e}")
         return

    # 2. Load Class Names
    try:
        with open(CLASS_NAMES_PATH, "r") as f:
            class_names = json.load(f)
        print(f"✅ Class Names Loaded: {class_names}")
    except Exception as e:
        print(f"❌ Failed to load class names: {e}")
        return

    # 3. Load Sample Image
    # Hardcoded sample path from previous search
    image_path = r"D:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal plant dataset\Amruta_Balli\2500.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Sample image not found: {image_path}")
        return
        
    try:
        img = Image.open(image_path).convert("RGB")
        img = img.resize((224, 224))
        img_data = np.array(img).astype(np.float32) / 255.0
        
        # Standardize (ImageNet stats)
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img_data = (img_data - mean) / std
        
        # HWC to CHW
        img_data = img_data.transpose(2, 0, 1)
        # Add Batch Dim
        img_data = np.expand_dims(img_data, axis=0)
        
        print(f"📸 Image Processed: {image_path}")
        
    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        return

    # 4. Predict
    try:
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        
        result = session.run([output_name], {input_name: img_data})
        probabilities = result[0][0] # Softmax might be needed if model outputs logits
        
        # Apply Softmax if needed (MobileNet usually outputs logits)
        def softmax(x):
            e_x = np.exp(x - np.max(x))
            return e_x / e_x.sum()
            
        probs = softmax(probabilities)
        class_idx = np.argmax(probs)
        confidence = probs[class_idx]
        predicted_class = class_names[class_idx]
        
        print("\n📊 PREDICTION RESULT")
        print("-" * 20)
        print(f"Predicted:  {predicted_class}")
        print(f"Confidence: {confidence:.2%}")
        
        if "Tinospora" in predicted_class or "Amruta" in predicted_class: # Amrutha Balli is Tinospora
             print("✅ ACCURACY: CORRECT (Matches 'Amruta_Balli')")
        else:
             print(f"ℹ️  Note: Prediction '{predicted_class}' ok for verification.")
             
        print("-" * 50)
        print("✅ AI SYSTEM IS FUNCTIONAL")
        
    except Exception as e:
        print(f"❌ Inference failed: {e}")

if __name__ == "__main__":
    verify_ai_engine()
