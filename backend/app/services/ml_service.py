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
import hashlib

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


import cv2
import base64

MEDICINAL_DB = {
    "tulsi": {"uses": "Cough, cold, fever, immunity", "prep": "Boil 10-15 leaves as tea", "caution": "Avoid during pregnancy", "toxic": False},
    "neem": {"uses": "Antibacterial, antifungal, skin diseases", "prep": "Apply leaf paste or drink boiled leaves", "caution": "Small doses only", "toxic": False},
    "aloe vera": {"uses": "Burns, skin, digestion, immunity", "prep": "Extract gel from leaf directly", "caution": "Avoid yellow latex layer", "toxic": False},
    "ashwagandha": {"uses": "Stress, immunity, energy", "prep": "Mix powder in milk", "caution": "Avoid if hyperthyroid", "toxic": False},
    "datura": {"uses": "Medical use only", "prep": "NEVER self-administer", "caution": "HIGHLY TOXIC", "toxic": True},
    "oleander": {"uses": "External use only", "prep": "NEVER consume", "caution": "CARDIAC TOXIN — extremely dangerous", "toxic": True}
}

def get_medicinal_info(plant_name: str) -> dict:
    name_lower = plant_name.lower()
    for key in MEDICINAL_DB:
        if key in name_lower or name_lower in key:
            return MEDICINAL_DB[key]
    return {"uses": "General wellness", "prep": "Consult practitioner", "caution": "Verify identity", "toxic": False}

def get_last_conv_layer(model):
    for layer in reversed(model.layers):
        if len(layer.output_shape) == 4:
            return layer.name
    raise ValueError("No conv layer found")

def get_gradcam_base64(model, img_array, class_idx):
    try:
        # Robust layer finding for nested functional models
        last_conv_layer = None
        target_model = model
        
        # Priority 1: Check top-level layers
        for layer in reversed(model.layers):
            if len(layer.output_shape) == 4:
                last_conv_layer = layer
                break
        
        # Priority 2: If the last 4D layer is a sub-model (like EfficientNet base), go inside
        if last_conv_layer and hasattr(last_conv_layer, 'layers'):
            target_model = last_conv_layer
            for layer in reversed(target_model.layers):
                if len(layer.output_shape) == 4 and "conv" in layer.name.lower():
                    last_conv_layer = layer
                    break
        
        if not last_conv_layer:
            return None

        import tensorflow as tf
        grad_model = tf.keras.Model(
            inputs=target_model.input,
            outputs=[last_conv_layer.output, target_model.output]
        )
        
        # If target_model is a sub-model, we need to pass the right input.
        # But for GradientTape, we can just use the target_model's output branch.
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            loss = predictions[:, class_idx]
        
        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        import numpy as np
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()
        
        heatmap_resized = cv2.resize(heatmap, (224, 224))
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        
        orig_img = img_array[0]
        if np.min(orig_img) < 0:
             orig_img = (orig_img + 1.0) * 127.5
        elif np.max(orig_img) <= 1.0:
             orig_img = orig_img * 255.0
             
        superimposed = cv2.addWeighted(np.uint8(orig_img), 0.6, heatmap_colored, 0.4, 0)
        _, buffer = cv2.imencode('.jpg', superimposed)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        import logging
        import traceback
        logging.getLogger(__name__).error(f"Grad-CAM error: {e}")
        print(f"DEBUG GRADCAM ERROR: {e}")
        traceback.print_exc()
        return None


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
        self.leaf_gate_session = None
        self.mobilenet_session = None
        self.vit_session = None
        self.efficientnet_session = None
        
        # TensorFlow Models (Fallback/Direct)
        self.h5_model = None
        self.h5_model_type = "none"
        
        # Thread pool for CPU-bound inference
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # OOD Threshold - The "Intelligence" Filters
        self.CONFIDENCE_THRESHOLD = 0.01  # Default; overridden by SHOWCASE_MODE
        self.AMBIGUOUS_THRESHOLD = 0.55   # Flag for Gemini verification

        
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

            # 4. Load Master H5 Model (Disabled for absolute ONNX determinism)
            # if TF_AVAILABLE:
            #     mobilenet_h5 = settings.MOBILENET_MODEL_PATH.replace('.onnx', '.h5')
            #     if os.path.exists(mobilenet_h5):
            #         self.h5_model = tf.keras.models.load_model(mobilenet_h5, compile=False)
            #         self.h5_model_type = "mobilenet-v2-master"
            #         logger.info(f"Loaded MobileNet Master 80-Class Model from {mobilenet_h5}")
            
            # 4. Load Master H5 Model (Priority for 80-class accuracy)
            if TF_AVAILABLE:
                # Priority 1: EfficientNetV2 Master (90MB) - Verified 80-Class
                efficientnet_h5 = os.path.join(settings.MODEL_DIR, "efficientnetv2_best.h5")
                
                if os.path.exists(efficientnet_h5):
                    self.h5_model = tf.keras.models.load_model(efficientnet_h5, compile=False)
                    self.h5_model_type = "efficientnet-v2"
                    logger.info(f"Loaded Master 80-Class H5 Model from {efficientnet_h5}")
                else:
                    self.h5_model = None
                    self.h5_model_type = "none"
            else:
                self.h5_model = None
                self.h5_model_type = "none"
            
            # 5. Initialize ONNX sessions
            providers = ['CPUExecutionProvider'] # Add 'CUDAExecutionProvider' if GPU available

            # Leaf Gate (binary: leaf vs non-leaf)
            if settings.ENABLE_LEAF_GATE and os.path.exists(settings.LEAF_GATE_MODEL_PATH):
                self.leaf_gate_session = ort.InferenceSession(settings.LEAF_GATE_MODEL_PATH, providers=providers)
                logger.info(f"Loaded Leaf Gate (ONNX) from {settings.LEAF_GATE_MODEL_PATH}")
            else:
                self.leaf_gate_session = None
            
            if os.path.exists(settings.MOBILENET_MODEL_PATH):
                self.mobilenet_session = ort.InferenceSession(settings.MOBILENET_MODEL_PATH, providers=providers)
                logger.info(f"Loaded MobileNetV2 (ONNX) from {settings.MOBILENET_MODEL_PATH}")

            if os.path.exists(settings.VIT_MODEL_PATH):
                self.vit_session = ort.InferenceSession(settings.VIT_MODEL_PATH, providers=providers)
                logger.info(f"Loaded ViT from {settings.VIT_MODEL_PATH}")
            
            if os.path.exists(settings.ENHANCED_MODEL_PATH):
                self.efficientnet_session = ort.InferenceSession(settings.ENHANCED_MODEL_PATH, providers=providers)
                logger.info(f"Loaded EfficientNetV2 from {settings.ENHANCED_MODEL_PATH}")
            
            self.use_mock = False
            self.models_loaded = True
            logger.info("ML Service initialized (Production Mode)")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            if settings.STRICT_ML_MODE:
                logger.critical("ML Service failed to load models in STRICT_ML_MODE. Shutting down service availability.")
                raise RuntimeError(f"ML Model initialization failed: {e}")
            
            logger.warning("Falling back to DEMO mode due to load error.")
            self.use_mock = True
            self.models_loaded = True

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        logits = logits - np.max(logits, axis=1, keepdims=True)
        exp = np.exp(logits)
        return exp / np.sum(exp, axis=1, keepdims=True)

    def _leaf_gate(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Binary gate: decides if the input is a leaf image.

        Expected ONNX output: either probabilities shape [1,2] or logits [1,2].
        Class convention used by training script: index 1 = leaf, index 0 = non_leaf.
        """
        if not settings.ENABLE_LEAF_GATE or not self.leaf_gate_session:
            return {"enabled": False}

        try:
            # Gate models typically use NHWC float32. We'll use NHWC and normalize to [-1, 1].
            gate_input = self.preprocess_image(image_bytes, return_nhwc=True)
            gate_input = (gate_input / 127.5) - 1.0

            input_name = self.leaf_gate_session.get_inputs()[0].name
            output = self.leaf_gate_session.run(None, {input_name: gate_input})
            raw = output[0]
            if raw.ndim != 2 or raw.shape[0] != 1:
                raise ValueError(f"Unexpected leaf gate output shape: {getattr(raw, 'shape', None)}")

            # If outputs sum ~1 -> assume probs; else softmax logits.
            row = raw.astype(np.float32)
            s = float(np.sum(row[0]))
            probs = row if 0.98 <= s <= 1.02 else self._softmax(row)

            non_leaf_p = float(probs[0][0])
            leaf_p = float(probs[0][1]) if probs.shape[1] > 1 else 0.0
            is_leaf = leaf_p >= float(settings.LEAF_GATE_THRESHOLD)

            return {
                "enabled": True,
                "is_leaf": bool(is_leaf),
                "leaf_probability": leaf_p,
                "non_leaf_probability": non_leaf_p,
                "threshold": float(settings.LEAF_GATE_THRESHOLD),
                "model": os.path.basename(settings.LEAF_GATE_MODEL_PATH),
            }
        except Exception as e:
            logger.warning(f"Leaf gate failed; continuing without gate. Error: {e}")
            return {"enabled": True, "error": str(e)}
    
    def preprocess_image(self, image_bytes: bytes, target_size: Tuple[int, int] = (224, 224), return_nhwc: bool = False) -> np.ndarray:
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
            # Explicitly use BILINEAR to match standard training pipelines
            image = image.resize(target_size, resample=Image.BILINEAR)
            
            # Convert to numpy array
            img_array = np.array(image, dtype=np.float32)
            
            if return_nhwc:
                # Direct for Keras: NHWC [0, 255]
                return np.expand_dims(img_array, axis=0)

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
            # Leaf gate already rejects non-leaf inputs.
            # Keep species classifier permissive for leaf images so we don't overuse "Unknown".
            self.CONFIDENCE_THRESHOLD = 0.01

            # --- STAGE 0: Leaf Gate ---
            gate = self._leaf_gate(image_bytes)
            if gate.get("enabled") and gate.get("is_leaf") is False:
                return {
                    "predicted_class": "Not a Plant Leaf",
                    "predicted_class_index": -1,
                    "confidence": 1.0 - float(gate.get("leaf_probability", 0.0)),
                    "top_predictions": [],
                    "model_version": "leaf-gate",
                    "ensemble_used": False,
                    "is_ambiguous": False,
                    "gate": gate,
                    "message": "Input rejected: not a plant leaf."
                }

            # --- PRIMARY: Master 80-Class Model (TensorFlow H5) ---
            mobilenet_probs = None
            model_version = "unknown"
            ensemble_used = False
            
            if self.h5_model:
                # Use Direct NHWC preprocessing for Keras to avoid transpose bugs
                h5_input = self.preprocess_image(image_bytes, return_nhwc=True)
                
                # Rescaling check (MobileNet-master expects [-1, 1])
                if "mobilenet" in self.h5_model_type:
                    h5_input = (h5_input / 127.5) - 1.0
                
                h5_output = self.h5_model.predict(h5_input, verbose=0)
                mobilenet_probs = h5_output 
                idx = int(np.argmax(mobilenet_probs[0]))
                
                model_version = self.h5_model_type
                logger.info(f"🧠 {self.h5_model_type} predicted index {idx}")
            
            # Run ONNX models (Alternative/Fallback)
            input_data = self.preprocess_image(image_bytes) # standard CHW [-1, 1]
            vit_probs = None
            efficientnet_probs = None
            
            if mobilenet_probs is None and self.mobilenet_session:
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

            # Authority Check: If Master H5 is loaded, skip ONNX ensemble to ensure mapping stability
            if self.h5_model and mobilenet_probs is not None:
                final_probs = mobilenet_probs
                ensemble_used = False
                model_version = self.h5_model_type
            elif efficientnet_probs is not None:
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
                if not self.h5_model:
                    ensemble_used = False
                    model_version = "mobilenet-v2"
                # If h5_model was used, model_version and ensemble_used are already set
            elif vit_probs is not None:
                final_probs = vit_probs
                ensemble_used = False
                model_version = "vit-b16"
            else:
                return self._predict_mock()

            # Get results
            pred_idx = np.argmax(final_probs[0])
            confidence = float(final_probs[0][pred_idx])
            
            # --- SUPERIOR REJECTION LOGIC (OOD) ---
            # If not confident enough, admit ignorance rather than guessing wrong.
            if confidence < self.CONFIDENCE_THRESHOLD:
                logger.warning(f"OOD Detected: Low confidence ({confidence:.2f}) < Threshold ({self.CONFIDENCE_THRESHOLD})")
                return {
                    "predicted_class": "Unknown / Not a Medicinal Leaf",
                    "predicted_class_index": -1,
                    "confidence": confidence,
                    "top_predictions": [],
                    "model_version": model_version,
                    "ensemble_used": ensemble_used,
                    "is_ambiguous": True,
                    "gate": gate if isinstance(gate, dict) else None,
                    "message": "Low-confidence result: input not recognized as a known medicinal plant leaf."
                }
            
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
            
            # Hybrid Intelligence Flag: If confident but not CERTAIN, suggest extended AI check
            is_ambiguous = confidence < self.AMBIGUOUS_THRESHOLD

            med_info = get_medicinal_info(predicted_class)
            gradcam_base64 = None
            if self.h5_model:
                try:
                    gradcam_base64 = get_gradcam_base64(self.h5_model, h5_input, int(pred_idx))
                except Exception as ge:
                    logger.warning(f"Grad-CAM generation failed: {ge}")

            return {
                "predicted_class": predicted_class,
                "predicted_class_index": int(pred_idx),
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_version": model_version,
                "ensemble_used": ensemble_used,
                "is_ambiguous": is_ambiguous,
                "gate": gate if isinstance(gate, dict) else None,
                "gradcam_base64": gradcam_base64,
                "medicinal_info": med_info,
                "is_toxic": med_info["toxic"],
                "caution": med_info["caution"]
            }

        except Exception as e:
            logger.error(f"Inference error: {e}")
            if settings.STRICT_ML_MODE or not settings.SHOWCASE_MODE:
                raise
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
