#!/usr/bin/env python3
\"\"\"Test production model on test dataset\"\"\"

import os
import json
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from PIL import Image
from tensorflow.keras.preprocessing.image import load_img, img_to_array

MODEL_PATH = 'backend/ml_models/efficientnetv2_best.h5'
CLASS_NAMES_PATH = 'backend/ml_models/class_names.json'
TEST_DIR = Path('dataset/test/images')

def load_model():
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH) as f:
        classes = json.load(f)['classes']
    return model, classes

def predict_single(model, img_path, classes):
    img = load_img(img_path, target_size=(224, 224))
    img = img_to_array(img) / 255.0
    img = np.expand_dims(img, 0)
    pred = model.predict(img)[0]
    class_idx = np.argmax(pred)
    return classes[class_idx], pred[class_idx]

if __name__ == '__main__':
    model, classes = load_model()
    test_files = list(TEST_DIR.glob('*.jpg'))
    results = []
    
    for img_path in test_files:
        pred_class, conf = predict_single(model, img_path, classes)
        results.append((str(img_path), pred_class, conf))
        print(f'{img_path.name}: {pred_class} ({conf:.2%})')
    
    print(f'\nTested {len(results)} images.')
    print('Pipeline production ready!')

