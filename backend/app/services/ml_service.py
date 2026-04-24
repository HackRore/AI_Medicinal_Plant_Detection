import onnxruntime as ort
import numpy as np
import cv2
import base64
import json
import time
import os
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(_HERE))

def _find(fname, dirs):
    for d in dirs:
        p = os.path.normpath(os.path.join(_BACKEND, d, fname))
        if os.path.exists(p):
            return p
    return fname

MODEL_PATH = _find('plantoai_model.onnx', ['ml_models'])
CLASS_PATH = _find('class_names.json',    ['app/data'])
KB_PATH    = _find('medicinal_knowledge.json', ['app/data'])

class MLService:
    def __init__(self):
        try:
            with open(CLASS_PATH, encoding='utf-8') as f:
                self.class_names = json.load(f)
            with open(KB_PATH, encoding='utf-8') as f:
                self.kb = json.load(f)
            
            self.sess = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
            self.model_loaded = True
            logger.info("Neural Engine: ONLINE")
        except Exception as e:
            self.model_loaded = False
            self.class_names = []
            self.kb = {}
            logger.error(f"Neural Engine: OFFLINE - {e}")

    def predict(self, image_bytes):
        try:
            # Inline import to bypass any weird module loading issues
            from PIL import Image, ImageOps
            start_time = time.time()
            
            img = Image.open(BytesIO(image_bytes)).convert('RGB')
            img = img.resize((224, 224))
            
            x = np.array(img).astype(np.float32) / 255.0
            x = np.transpose(x, (2, 0, 1))
            x = np.expand_dims(x, axis=0)
            
            input_name = self.sess.get_inputs()[0].name
            preds = self.sess.run(None, {input_name: x})[0][0]
            
            idx = int(np.argmax(preds))
            conf = float(preds[idx])
            
            # Robust extraction: handles both ["Aloe Vera"] and [{"name": "Aloe Vera"}]
            raw_class = self.class_names[idx] if idx < len(self.class_names) else "Unknown"
            if isinstance(raw_class, dict):
                name = raw_class.get("name", "Unknown")
            else:
                name = str(raw_class)
            
            return {
                "success": True,
                "predicted_class": name,
                "confidence": conf,
                "processing_time": time.time() - start_time,
                "knowledge": self.kb.get(name, {})
            }
        except Exception as e:
            return {"success": False, "error": "Inference Error", "details": str(e)}

ml_service = MLService()
def get_ml_service(): return ml_service
