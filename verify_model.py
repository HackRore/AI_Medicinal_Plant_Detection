import tensorflow as tf
import numpy as np
from PIL import Image
import json
import requests
from io import BytesIO
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

model = tf.keras.models.load_model(
    r'C:\Users\Dell\Downloads\HackRore\AI_Medicinal_Plant_Detection\backend\ml_models\efficientnetv2_best.h5',
    compile=False
)

with open(r'C:\Users\Dell\Downloads\HackRore\AI_Medicinal_Plant_Detection\backend\ml_models\class_names.json') as f:
    classes = json.load(f)

print(f"Classes: {len(classes)}")
print(f"First 10: {classes[:10]}")

# Test with real image
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Tulsi_plant2.jpg/320px-Tulsi_plant2.jpg"
img = Image.open(BytesIO(requests.get(url).content)).convert('RGB').resize((224,224))
arr = np.expand_dims(np.array(img).astype(np.float32), axis=0)

preds = model.predict(arr, verbose=0)
top3 = np.argsort(preds[0])[-3:][::-1]

print("\nTulsi leaf test:")
for i in top3:
    print(f"  {classes[i]:30}: {preds[0][i]*100:.1f}%")
