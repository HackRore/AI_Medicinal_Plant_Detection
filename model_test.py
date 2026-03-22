import tensorflow as tf
import numpy as np
from PIL import Image

model = tf.keras.models.load_model(
    r'd:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5',
    compile=False
)
print("Model loaded successfully")
print(f"Input shape: {model.input_shape}")
print(f"Output classes: {model.output_shape}")
print(f"Total parameters: {model.count_params():,}")

import json
with open(r'd:\PROJECT STAGE 1\backend\ml_models\class_names.json') as f:
    classes = json.load(f)
print(f"Class names loaded: {len(classes)} classes")
print(f"First 10 classes: {classes[:10]}")
