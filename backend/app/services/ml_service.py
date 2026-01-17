"""
ML Service
Handles model loading, inference, and predictions using ONNX Runtime.
Supports MobileNetV2 and Vision Transformer ensemble.
"""

import os
import json
import numpy as np
from typing import Dict, List, Tuple, Any
from PIL import Image
import io
import logging
import concurrent.futures

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class MLService:
    """Machine Learning inference service using ONNX Runtime"""
    
    def __init__(self):
        self.models_loaded = False
        self.use_mock = False
        self.class_names = []
        
        # ONNX Sessions
        self.mobilenet_session = None
        self.vit_session = None
        self.efficientnet_session = None
        
        # Thread pool for CPU-bound inference
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
    def load_models(self):
        """Load ML models and class names"""
        try:
            # 1. Load class names
            if os.path.exists(settings.CLASS_NAMES_PATH):
                with open(settings.CLASS_NAMES_PATH, 'r') as f:
                    self.class_names = json.load(f)
                logger.info(f"Loaded {len(self.class_names)} class names")
            else:
                logger.warning("Class names file not found. Using default mock classes.")
                self.class_names = [
                    "Ocimum_tenuiflorum", "Azadirachta_indica", "Aloe_vera",
                    "Mentha", "Tinospora_cordifolia"
                ]

            # 2. Check dependencies
            if not ONNX_AVAILABLE:
                logger.warning("ONNX Runtime not installed. Falling back to DEMO mode.")
                self.use_mock = True
                self.models_loaded = True
                return

            # 3. Load ONNX models
            model_files_exist = (
                os.path.exists(settings.MOBILENET_MODEL_PATH) or 
                os.path.exists(settings.VIT_MODEL_PATH)
            )
            
            if not model_files_exist:
                logger.warning(f"Model files not found in {settings.MODEL_DIR}. Falling back to DEMO mode.")
                self.use_mock = True
                self.models_loaded = True
                return

            # Initialize sessions
            providers = ['CPUExecutionProvider'] # Add 'CUDAExecutionProvider' if GPU available
            
            if os.path.exists(settings.MOBILENET_MODEL_PATH):
                self.mobilenet_session = ort.InferenceSession(settings.MOBILENET_MODEL_PATH, providers=providers)
                logger.info(f"Loaded MobileNetV2 from {settings.MOBILENET_MODEL_PATH}")

            if os.path.exists(settings.VIT_MODEL_PATH):
                self.vit_session = ort.InferenceSession(settings.VIT_MODEL_PATH, providers=providers)
                logger.info(f"Loaded ViT from {settings.VIT_MODEL_PATH}")
            
            if os.path.exists(settings.ENHANCED_MODEL_PATH):
                self.efficientnet_session = ort.InferenceSession(settings.ENHANCED_MODEL_PATH, providers=providers)
                logger.info(f"Loaded EfficientNetV2 from {settings.ENHANCED_MODEL_PATH}")
            
            self.use_mock = False
            self.models_loaded = True
            logger.info("ML Sercice initialized (Production Mode)")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            if settings.STRICT_ML_MODE:
                logger.critical("ML Service failed to load models in STRICT_ML_MODE. Shutting down service availability.")
                raise RuntimeError(f"ML Model initialization failed: {e}")
            
            logger.warning("Falling back to DEMO mode due to load error.")
            self.use_mock = True
            self.models_loaded = True
    
    def preprocess_image(self, image_bytes: bytes, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """
        Preprocess image for model inference
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize
            image = image.resize(target_size)
            
            # Convert to numpy array
            img_array = np.array(image, dtype=np.float32)
            
            # Normalize (0-1 range to -1 to 1 range usually for MobileNet, or specific mean/std)
            # Assuming standard MobileNet/ViT preprocessing: (x / 127.5) - 1.0
            img_array = (img_array / 127.5) - 1.0
            
            # HWC to CHW format (required by PyTorch/ONNX converted models)
            img_array = np.transpose(img_array, (2, 0, 1))
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            raise ValueError(f"Error preprocessing image: {e}")
    
    def _predict_mock(self) -> Dict:
        """Generate a mock prediction result"""
        import random
        predicted_class_idx = random.randint(0, len(self.class_names) - 1)
        confidence = random.uniform(0.75, 0.98)
        
        top_predictions = []
        for i in range(min(5, len(self.class_names))):
            idx = (predicted_class_idx + i) % len(self.class_names)
            conf = confidence - (i * 0.1)
            top_predictions.append({
                "class_name": self.class_names[idx],
                "confidence": max(0.1, conf)
            })
            
        return {
            "predicted_class": self.class_names[predicted_class_idx],
            "predicted_class_index": predicted_class_idx,
            "confidence": confidence,
            "top_predictions": top_predictions,
            "model_version": "demo-v1.0",
            "ensemble_used": False
        }

    def _run_inference(self, image_bytes: bytes) -> Dict:
        """Run actual inference (executed in thread pool)"""
        if self.use_mock:
            if settings.STRICT_ML_MODE:
                raise RuntimeError("ML Service is in DEMO mode but STRICT_ML_MODE is enabled. Rejecting prediction.")
            return self._predict_mock()

        try:
            input_data = self.preprocess_image(image_bytes)
            
            mobilenet_probs = None
            vit_probs = None
            
            # Run MobileNetV2
            if self.mobilenet_session:
                input_name = self.mobilenet_session.get_inputs()[0].name
                mobilenet_output = self.mobilenet_session.run(None, {input_name: input_data})
                mobilenet_logits = mobilenet_output[0]
                # Softmax
                mobilenet_probs = np.exp(mobilenet_logits) / np.sum(np.exp(mobilenet_logits), axis=1, keepdims=True)
            
            # Run ViT
            if self.vit_session:
                input_name = self.vit_session.get_inputs()[0].name
                # ViT might expect different preprocessing, but assuming consistent pipeline here
                vit_output = self.vit_session.run(None, {input_name: input_data})
                vit_logits = vit_output[0]
                vit_probs = np.exp(vit_logits) / np.sum(np.exp(vit_logits), axis=1, keepdims=True)
            
            # Run EfficientNetV2 (Primary for Enhanced Intelligence)
            efficientnet_probs = None
            if self.efficientnet_session:
                input_name = self.efficientnet_session.get_inputs()[0].name
                # EfficientNetV2 internally handles rescaling, so we pass raw uint8-like float [0, 255]
                # Re-preprocess for EfficientNetV2 if needed or assuming internal scaling
                eff_input = (input_data + 1.0) * 127.5 # Back to [0, 255]
                eff_output = self.efficientnet_session.run(None, {input_name: eff_input})
                eff_logits = eff_output[0]
                efficientnet_probs = np.exp(eff_logits) / np.sum(np.exp(eff_logits), axis=1, keepdims=True)

            # Ensemble Logic (Weighted towards EfficientNetV2)
            if efficientnet_probs is not None:
                if mobilenet_probs is not None:
                    final_probs = (efficientnet_probs * 0.7) + (mobilenet_probs * 0.3)
                    ensemble_used = True
                    model_version = "efficientnet-mobilenet-ensemble"
                else:
                    final_probs = efficientnet_probs
                    ensemble_used = False
                    model_version = "efficientnet-v2-s"
            elif mobilenet_probs is not None and vit_probs is not None:
                final_probs = (mobilenet_probs + vit_probs) / 2.0
                ensemble_used = True
                model_version = "ensemble-v1.0"
            elif mobilenet_probs is not None:
                final_probs = mobilenet_probs
                ensemble_used = False
                model_version = "mobilenet-v2"
            elif vit_probs is not None:
                final_probs = vit_probs
                ensemble_used = False
                model_version = "vit-b16"
            else:
                return self._predict_mock()

            # Get results
            pred_idx = np.argmax(final_probs[0])
            confidence = float(final_probs[0][pred_idx])
            
            # Top 5
            top_k_indices = np.argsort(final_probs[0])[::-1][:5]
            top_predictions = []
            for idx in top_k_indices:
                if idx < len(self.class_names):
                    top_predictions.append({
                        "class_name": self.class_names[idx],
                        "confidence": float(final_probs[0][idx])
                    })
            
            predicted_class = self.class_names[pred_idx] if pred_idx < len(self.class_names) else f"Class_{pred_idx}"

            return {
                "predicted_class": predicted_class,
                "predicted_class_index": int(pred_idx),
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_version": model_version,
                "ensemble_used": ensemble_used
            }

        except Exception as e:
            logger.error(f"Inference error: {e}")
            return self._predict_mock()

    def predict(self, image_bytes: bytes) -> Dict:
        """
        Predict plant species from image
        """
        if not self.models_loaded:
            self.load_models()
        
        # Run in thread pool to avoid blocking async event loop
        # Image processing and inference are CPU bound
        try:
            future = self.executor.submit(self._run_inference, image_bytes)
            return future.result()
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction service failure: {e}")

    def predict_batch(self, images: List[bytes]) -> List[Dict]:
        """Batch prediction"""
        results = []
        # Could be optimized with batch inference in ONNX, but loop is safer for mixed inputs
        for img_bytes in images:
            try:
                result = self.predict(img_bytes)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "predicted_class": None,
                    "confidence": 0.0
                })
        return results

# Global ML service instance
ml_service = MLService()

def get_ml_service() -> MLService:
    """Get ML service instance"""
    return ml_service
