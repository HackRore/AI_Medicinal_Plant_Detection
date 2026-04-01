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
    """Production-grade ML service using ONNX Runtime for stable CPU inference"""
    
    def __init__(self):
        self.session = None
        self.input_name = None
        self.class_names = []
        self._cache = OrderedDict()
        self.CACHE_SIZE = 15
        self.initialized = False
        
        # Standard configs
        self.INPUT_SIZE = 224
        self.CONFIDENCE_THRESHOLD = 0.45

    def _get_image_hash(self, image_bytes: bytes) -> str:
        return hashlib.sha256(image_bytes).hexdigest()

    def load_resources(self):
        """Lazy load ML weights and metadata"""
        if self.initialized:
            return

        try:
            # 1. Load class names v3 (Superior Triple Intelligence)
            v3_class_path = os.path.join(settings.MODEL_DIR, "class_names_v3.json")
            class_path = v3_class_path if os.path.exists(v3_class_path) else os.path.join(settings.MODEL_DIR, "class_names.json")
            
            if os.path.exists(class_path):
                with open(class_path, 'r') as f:
                    self.class_names = json.load(f)
                logger.info(f"🧬 ML Service: Loaded {len(self.class_names)} classes from {os.path.basename(class_path)}")
            else:
                self.class_names = [f"Species_{i}" for i in range(81)]
            
            # 2. Load Model (Priority: PyTorch v3 -> ONNX -> Fallbacks)
            v3_model_path = os.path.join(settings.MODEL_DIR, "model_v3.pth")
            v3_onnx_path = os.path.join(settings.MODEL_DIR, "model_v3.onnx")
            onnx_path = v3_onnx_path if os.path.exists(v3_onnx_path) else os.path.join(settings.MODEL_DIR, "efficientnetv2.onnx")
            
            if os.path.exists(v3_model_path):
                import torch
                from torchvision import models
                import torch.nn as nn
                
                # Dynamic architecture reconstruction (MobileNetV2 v3)
                self.torch_model = models.mobilenet_v2()
                n_inputs = self.torch_model.classifier[1].in_features
                self.torch_model.classifier[1] = nn.Sequential(
                    nn.Linear(n_inputs, 512),
                    nn.ELU(),
                    nn.Linear(512, len(self.class_names))
                )
                self.torch_model.load_state_dict(torch.load(v3_model_path, map_location='cpu'))
                self.torch_model.eval()
                self.use_torch = True
                logger.info("🚀 ML Service: Loaded Superior PyTorch Model (v3)")
            
            elif os.path.exists(onnx_path):
                self.session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
                self.input_name = self.session.get_inputs()[0].name
                self.use_torch = False
                logger.info(f"🚀 ML Service: Loaded ONNX model {os.path.basename(onnx_path)}")
            else:
                logger.error("❌ Critical: No high-performance model found!")
                self.session = None
                self.use_torch = False
            
            self.initialized = True
        except Exception as e:
            logger.error(f"❌ Failed to load ML resources: {e}")
            self.initialized = True

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Preprocess for EfficientNetV2/MobileNetV2 style models"""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((self.INPUT_SIZE, self.INPUT_SIZE), Image.LANCZOS)
        arr = np.array(img, dtype=np.float32) / 255.0
        
        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        arr = (arr - mean) / std
        
        return np.expand_dims(arr, axis=0).astype(np.float32)

    def predict(self, image_bytes: bytes) -> Dict:
        """Prediction with timing and caching"""
        start_time = time.time()
        img_hash = self._get_image_hash(image_bytes)

        # 1. Cache Check
        if img_hash in self._cache:
            result = self._cache.pop(img_hash)
            self._cache[img_hash] = result
            result["cache_hit"] = True
            return result

        # 2. Lazy Load
        if not self.initialized:
            self.load_resources()

        if self.session is None and not getattr(self, 'use_torch', False):
            return {"error": "Model not loaded", "confidence": 0.0}

        try:
            # 3. Preprocessing
            pre_start = time.time()
            processed_img = self.preprocess(image_bytes)
            preprocessing_time = time.time() - pre_start

            # 4. Inference
            inf_start = time.time()
            
            if getattr(self, 'use_torch', False):
                import torch
                with torch.no_grad():
                    # Align to PyTorch NCHW format
                    torch_img = np.transpose(processed_img, (0, 3, 1, 2))
                    inputs = torch.from_numpy(torch_img)
                    outputs = self.torch_model(inputs)
                    predictions = torch.nn.functional.softmax(outputs, dim=1)[0].numpy()
            else:
                outputs = self.session.run(None, {self.input_name: processed_img})
                raw_preds = outputs[0][0]
                exp_preds = np.exp(raw_preds - np.max(raw_preds))
                predictions = exp_preds / exp_preds.sum()
                
            inference_time = time.time() - inf_start

            # 5. Build Result
            top_k_indices = np.argsort(predictions)[::-1][:5]
            top_predictions = []
            for idx in top_k_indices:
                top_predictions.append({
                    "class_name": self.class_names[idx] if idx < len(self.class_names) else f"Unknown_{idx}",
                    "confidence": float(predictions[idx])
                })

            best_idx = top_k_indices[0]
            confidence = float(predictions[best_idx])
            plant_name = self.class_names[best_idx] if best_idx < len(self.class_names) else "Unknown"

            result = {
                "predicted_class": plant_name,
                "predicted_class_index": int(best_idx),
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_version": "TripleIntelligence-v3" if getattr(self, 'use_torch', False) else "EfficientNetV2-ONNX",
                "inference_time": inference_time,
                "preprocessing_time": preprocessing_time,
                "cache_hit": False,
                "identified": confidence >= self.CONFIDENCE_THRESHOLD
            }

            self._cache[img_hash] = result
            if len(self._cache) > self.CACHE_SIZE:
                self._cache.popitem(last=False)

            return result

        except Exception as e:
            logger.error(f"Prediction failure: {e}")
            return {"error": str(e), "confidence": 0.0}

    def generate_gradcam(self, image_bytes: bytes) -> str:
        """Visual attention map using morphological saliency (TF-free)"""
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            orig_img = np.array(image.resize((224, 224)))
            
            # Saliency detection using OpenCV (Plant morphology focus)
            gray = cv2.cvtColor(orig_img, cv2.COLOR_RGB2GRAY)
            
            # Get edges and textures
            sob_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            sob_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            mag = cv2.magnitude(sob_x, sob_y)
            
            # Gaussian blur to create 'heatmap' effect
            heatmap = cv2.GaussianBlur(mag, (21, 21), 0)
            heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

            # Overlay
            superimposed = cv2.addWeighted(orig_img, 0.6, heatmap_color, 0.4, 0)
            
            _, buffer = cv2.imencode('.jpg', cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))
            return base64.b64encode(buffer).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Visualization error: {e}")
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
