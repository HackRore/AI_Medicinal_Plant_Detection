import tensorflow as tf
import numpy as np
import os
from PIL import Image
import io

MODEL_PATH = r"d:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5"
DATA_DIR = r"d:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"

def debug_api_logic():
    print("🧪 Debugging API Preprocessing Logic...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    img_path = os.path.join(DATA_DIR, "Aloevera", os.listdir(os.path.join(DATA_DIR, "Aloevera"))[0])
    image = Image.open(img_path).convert('RGB').resize((224, 224))
    
    # 1. API Preprocess
    img_array = np.array(image, dtype=np.float32)
    print(f"Shape 1 (Raw): {img_array.shape}") # (224, 224, 3)
    
    img_array = (img_array / 127.5) - 1.0 # [-1, 1]
    
    img_array = np.transpose(img_array, (2, 0, 1)) # CHW
    print(f"Shape 2 (CHW): {img_array.shape}") # (3, 224, 224)
    
    input_data = np.expand_dims(img_array, axis=0) # (1, 3, 224, 224)
    print(f"Shape 3 (Input): {input_data.shape}")
    
    # 2. API Inference Logic
    h5_input = np.transpose(input_data, (0, 2, 3, 1)) # Back to NHWC?
    print(f"Shape 4 (H5 Input): {h5_input.shape}") # (1, 224, 224, 3)
    
    h5_input = (h5_input + 1.0) * 127.5 # Back to [0, 255]
    h5_input = np.clip(h5_input, 0, 255)
    
    # 3. Predict
    preds = model.predict(h5_input, verbose=0)
    idx = np.argmax(preds[0])
    print(f"🎯 Final Prediction: Index {idx} (Conf: {preds[0][idx]*100:.1f}%)")

if __name__ == "__main__":
    debug_api_logic()
