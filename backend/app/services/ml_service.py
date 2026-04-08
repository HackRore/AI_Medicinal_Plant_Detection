import os
import json
import numpy as np
from typing import Dict, List, Tuple, Any
from PIL import Image
import io
import logging
import time
import hashlib
from collections import OrderedDict
import base64
import onnxruntime as ort
import cv2
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class MLService:
    """Production-grade ML service using EfficientNetV2-S for medicinal plant identification"""
    
    def __init__(self):
        self.session = None
        self.input_name = None
        self.class_names = []
        self.knowledge_base = {}
        self._cache = OrderedDict()
        self.CACHE_SIZE = 20
        self.initialized = False
        
        # Spec v2.0 Hardened Configs
        self.INPUT_SIZE = 224
        self.CONFIDENCE_THRESHOLD = 0.50  # Increased for production hardening

    def _get_image_hash(self, image_bytes: bytes) -> str:
        return hashlib.sha256(image_bytes).hexdigest()

    def load_resources(self):
        """Standardized resource loading for Spec v2.0"""
        if self.initialized:
            return

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, "model")
            data_dir = os.path.join(base_dir, "data")
            
            # 1. Load Knowledge Base
            kb_path = os.path.join(data_dir, "medicinal_knowledge.json")
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    self.knowledge_base = json.load(f)
                logger.info(f"🌿 ML Service: Loaded Knowledge Base ({len(self.knowledge_base)} species)")

            # 2. Load Class Index (13 Purely Medicinal Classes)
            idx_path = os.path.join(model_dir, "class_index.json")
            if os.path.exists(idx_path):
                with open(idx_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.class_names = data
                    else:
                        self.class_names = [data[str(i)] for i in range(len(data))]
                logger.info(f"🧬 ML Service: Loaded {len(self.class_names)} validated classes")

            # 3. Load ONNX Model (EfficientNetV2-S)
            onnx_path = os.path.join(model_dir, "efficientnetv2_medicinal.onnx")
            if not os.path.exists(onnx_path):
                onnx_path = os.path.join(model_dir, "efficientnetv2.onnx")

            if os.path.exists(onnx_path):
                self.session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
                self.input_name = self.session.get_inputs()[0].name
                logger.info(f"🚀 ML Service: Loaded Neural Engine {os.path.basename(onnx_path)}")
            else:
                logger.error("❌ Critical: No high-performance model found!")
                self.session = None

            self.initialized = True
        except Exception as e:
            logger.error(f"❌ Failed to load ML resources: {e}")
            self.initialized = True

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Preprocess for EfficientNetV2-S (384x384)"""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((self.INPUT_SIZE, self.INPUT_SIZE), Image.LANCZOS)
        arr = np.array(img, dtype=np.float32) / 255.0
        
        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        arr = (arr - mean) / std
        
        # Transpose to NCHW for ONNX EfficientNet
        arr = np.transpose(arr, (2, 0, 1))
        return np.expand_dims(arr, axis=0).astype(np.float32)

    def predict(self, image_bytes: bytes) -> Dict:
        """Production Prediction with Knowledge Integration"""
        start_time = time.time()
        img_hash = self._get_image_hash(image_bytes)

        if img_hash in self._cache:
            result = self._cache.pop(img_hash)
            self._cache[img_hash] = result
            result["cache_hit"] = True
            return result

        if not self.initialized:
            self.load_resources()

        if self.session is None:
            return {"error": "Neural engine not found. Verify model path.", "confidence": 0.0}

        try:
            pre_start = time.time()
            processed_img = self.preprocess(image_bytes)
            preprocessing_time = time.time() - pre_start

            inf_start = time.time()
            outputs = self.session.run(None, {self.input_name: processed_img})
            raw_preds = outputs[0][0]
            exp_preds = np.exp(raw_preds - np.max(raw_preds))
            predictions = exp_preds / exp_preds.sum()
            inference_time = time.time() - inf_start

            # Extract top 5
            top_k_indices = np.argsort(predictions)[::-1][:5]
            best_idx = top_k_indices[0]
            confidence = float(predictions[best_idx])
            plant_name = self.class_names[best_idx] if best_idx < len(self.class_names) else "Unknown"

            # Integrate Knowledge
            knowledge = self.knowledge_base.get(plant_name, {})
            
            result = {
                "predicted_class": plant_name,
                "confidence": confidence,
                "identified": confidence >= self.CONFIDENCE_THRESHOLD,
                "botanical_details": knowledge,
                "top_predictions": [
                    {"name": self.class_names[idx], "confidence": float(predictions[idx])}
                    for idx in top_k_indices if idx < len(self.class_names)
                ],
                "metadata": {
                    "inference_ms": round(inference_time * 1000, 2),
                    "model": "EfficientNetV2-S (G9-Hardened)",
                    "timestamp": time.time()
                }
            }

            self._cache[img_hash] = result
            if len(self._cache) > self.CACHE_SIZE:
                self._cache.popitem(last=False)

            return result

        except Exception as e:
            logger.error(f"Neural inference failure: {e}")
            return {"error": str(e), "confidence": 0.0}

    def generate_gradcam(self, image_bytes: bytes) -> str:
        """Morphological saliency map for visual verification (No-TF production build)"""
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            orig_img = np.array(img.resize((self.INPUT_SIZE, self.INPUT_SIZE)))
            
            # Saliency detection (Focus on leaf structure and veins)
            gray = cv2.cvtColor(orig_img, cv2.COLOR_RGB2GRAY)
            saliency = cv2.saliency.StaticSaliencyFineGrained_create()
            success, saliencyMap = saliency.computeSaliency(gray)
            
            heatmap = (saliencyMap * 255).astype("uint8")
            heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            
            # Overlay with highlight on structure
            superimposed = cv2.addWeighted(orig_img, 0.6, heatmap, 0.4, 0)
            
            _, buffer = cv2.imencode('.jpg', cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))
            return base64.b64encode(buffer).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Visualization failure: {e}")
            return None

# Singleton instance
ml_service = MLService()

def get_ml_service() -> MLService:
    return ml_service

def predict_plant(image_bytes: bytes) -> Dict:
    return ml_service.predict(image_bytes)

def get_gradcam_base64(image_bytes: bytes) -> str:
    """Helper for backward compatibility"""
    return ml_service.generate_gradcam(image_bytes)
