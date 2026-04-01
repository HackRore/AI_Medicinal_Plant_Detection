import os
import json
import numpy as np
from PIL import Image
import tensorflow as tf

# Paths
MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\model.tflite"
CLASS_NAMES_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"
REAL_UPLOADS_DIR = r"d:\PROJECT STAGE 1\backend\uploads"

def preprocess_neg1_pos1(image_path):
    img = Image.open(image_path).convert("RGB").resize((224, 224), Image.LANCZOS)
    arr = (np.array(img, dtype=np.float32) / 127.5) - 1.0
    return np.expand_dims(arr, axis=0)

def run_test():
    with open(CLASS_NAMES_PATH) as f:
        class_names = json.load(f)

    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    files = [f for f in os.listdir(REAL_UPLOADS_DIR) if f.endswith(".jpg")][:5]
    
    print(f"\n--- PlantoAI Multi-Sample Neural Benchmark (Scale [-1, 1]) ---")
    for filename in files:
        img_path = os.path.join(REAL_UPLOADS_DIR, filename)
        input_data = preprocess_neg1_pos1(img_path)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        preds = interpreter.get_tensor(output_details[0]['index'])[0]
        
        # Softmax if needed
        if not np.isclose(preds.sum(), 1.0, atol=1e-5):
            exp_preds = np.exp(preds - np.max(preds))
            preds = exp_preds / exp_preds.sum()

        top_idx = np.argmax(preds)
        print(f"\nFile: {filename}")
        print(f"Result: {class_names[top_idx]}")
        print(f"Confidence: {preds[top_idx]:.2%}")

if __name__ == "__main__":
    run_test()
