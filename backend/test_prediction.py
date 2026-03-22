import tensorflow as tf
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import json

print("Testing direct prediction script...")

model = tf.keras.models.load_model('ml_models/efficientnetv2_best.h5')
with open('ml_models/class_names.json') as f:
    classes = json.load(f)

url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Tulsi_plant2.jpg/320px-Tulsi_plant2.jpg'
content = requests.get(url).content

with open("tulsi_sample.jpg", "wb") as w:
    w.write(content)

img = Image.open(BytesIO(content)).convert('RGB').resize((224,224))
arr = np.expand_dims(np.array(img)/255.0, axis=0) # Normalize to [0,1]
preds = model.predict(arr, verbose=0)
top3 = np.argsort(preds[0])[-3:][::-1]

print('TOP 3 PREDICTIONS:')
for i in top3:
    print(f'  {classes[i]:30}: {preds[0][i]*100:.1f}%')
