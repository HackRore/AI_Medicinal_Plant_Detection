"""
Convert Keras (.h5) models to ONNX format
Required for the enhanced production ML Service
"""

import os
import tensorflow as tf
import tf2onnx
import onnx
from pathlib import Path

def convert_to_onnx(model_path, output_path):
    print(f"📦 Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)
    
    print("convert Transforming to ONNX...")
    spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)
    
    model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13)
    
    print(f"💾 Saving ONNX model to {output_path}...")
    with open(output_path, "wb") as f:
        f.write(model_proto.SerializeToString())
    
    print("✅ Conversion Success!")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent
    H5_PATH = BASE_DIR / "models" / "enhanced" / "efficientnetv2_best.h5"
    ONNX_PATH = BASE_DIR.parent / "backend" / "ml_models" / "efficientnetv2_best.onnx"
    
    if os.path.exists(H5_PATH):
        convert_to_onnx(H5_PATH, ONNX_PATH)
    else:
        print(f"❌ Error: Enhanced model not found at {H5_PATH}. Please run train_enhanced.py first.")
