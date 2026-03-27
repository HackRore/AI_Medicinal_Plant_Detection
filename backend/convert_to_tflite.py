import tensorflow as tf
import os

def convert():
    model_path = os.path.join("ml_models", "efficientnetv2_best.h5")
    tflite_path = os.path.join("ml_models", "model.tflite")

    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found")
        return

    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path, compile=False)

    print("Converting to TFLite (float16 quantization)...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    
    tflite_model = converter.convert()

    print(f"Saving TFLite model to {tflite_path}...")
    with open(tflite_path, "wb") as f:
        f.write(tflite_model)

    original_size = os.path.getsize(model_path) / (1024 * 1024)
    tflite_size = os.path.getsize(tflite_path) / (1024 * 1024)
    
    print(f"Original size: {original_size:.2f} MB")
    print(f"TFLite size: {tflite_size:.2f} MB")
    print(f"Reduction: {(1 - tflite_size/original_size)*100:.1f}%")

if __name__ == "__main__":
    convert()
