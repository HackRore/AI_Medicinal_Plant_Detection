import tensorflow as tf
import os

model_path = r"d:\PROJECT STAGE 1\backend\ml_models\mobilenetv2_best.h5"

if os.path.exists(model_path):
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        print(f"📊 Model Loaded: {model_path}")
        print(f"📐 Input Shape: {model.input_shape}")
        print(f"📐 Output Shape: {model.output_shape}")
        
        # Check if output is 80 or 81
        num_classes = model.output_shape[-1]
        print(f"🧠 Number of Classes: {num_classes}")
        
        if num_classes > 70:
            print("✅ This is the MASTER model!")
        else:
            print(f"⚠️ This is a {num_classes}-class placeholder.")
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")
else:
    print(f"❌ File not found: {model_path}")
