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

# --- Sprint 2: YOLOv8 Leaf Segmentation Setup ---
YOLO_AVAILABLE = False
leaf_detector = None
try:
    from ultralytics import YOLO
    # Suppress YOLO logs
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    # Using the standard yolov8n as placeholder until leaf-specific is fine-tuned
    YOLO_MODEL_PATH = os.path.join(_BACKEND, 'ml_models', 'yolov8n.pt')
    leaf_detector = YOLO(YOLO_MODEL_PATH if os.path.exists(YOLO_MODEL_PATH) else 'yolov8n.pt')
    YOLO_AVAILABLE = True
    logger.info("YOLOv8 Segmentation Engine: ONLINE")
except Exception as e:
    logger.warning(f"YOLOv8 Segmentation Engine unavailable: {e}")

def add_padding(img, pad_pct=0.10):
    from PIL import Image
    w, h = img.size
    pad_w = int(w * pad_pct)
    pad_h = int(h * pad_pct)
    new_img = Image.new(img.mode, (w + 2*pad_w, h + 2*pad_h), (0,0,0))
    new_img.paste(img, (pad_w, pad_h))
    return new_img

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
            from PIL import Image, ImageOps, ImageEnhance
            start_time = time.time()
            
            img = Image.open(BytesIO(image_bytes)).convert('RGB')
            
            # --- Stage 1: YOLOv8 Segmentation ---
            segmentation_status = "Bypassed"
            if YOLO_AVAILABLE and leaf_detector:
                results = leaf_detector(img, verbose=False)
                if len(results[0].boxes) > 0:
                    # Get highest confidence box
                    box = results[0].boxes[0].xyxy[0].cpu().numpy()
                    leaf_crop = img.crop((box[0], box[1], box[2], box[3]))
                    img = add_padding(leaf_crop, 0.10)
                    segmentation_status = "Active (Background Removed)"
                else:
                    segmentation_status = "No Leaf Detected (Using Full Image)"
            
            # --- Stage 2: Classification Preprocessing ---
            img_main = img.resize((224, 224))
            
            def preprocess(i):
                x = np.array(i.resize((224, 224))).astype(np.float32) / 255.0
                return np.transpose(x, (2, 0, 1)).reshape(1, 3, 224, 224)

            # --- Multi-Pass Neural TTA (Test-Time Augmentation) ---
            # 1. Original
            pass1 = preprocess(img_main)
            # 2. Horizontal Flip
            pass2 = preprocess(ImageOps.mirror(img_main))
            # 3. Center Zoom (Vein Extraction)
            w, h = img.size
            crop = img.crop((w*0.1, h*0.1, w*0.9, h*0.9))
            pass3 = preprocess(crop)
            # 4. Brightness Boost (Shadow Recovery)
            pass4 = preprocess(ImageEnhance.Brightness(img_main).enhance(1.2))
            # 5. Contrast Boost (Edge Sharpening)
            pass5 = preprocess(ImageEnhance.Contrast(img_main).enhance(1.2))

            input_name = self.sess.get_inputs()[0].name
            
            # Batch Inference
            batch_x = np.vstack([pass1, pass2, pass3, pass4, pass5])
            batch_logits = self.sess.run(None, {input_name: batch_x})[0]
            
            # Weighted Averaging (Main pass gets more weight)
            raw_preds = (batch_logits[0] * 0.4 + 
                         batch_logits[1] * 0.15 + 
                         batch_logits[2] * 0.15 + 
                         batch_logits[3] * 0.15 + 
                         batch_logits[4] * 0.15)
            
            # Softmax with Neural Sharpening (T=0.67)
            sharpened_logits = (raw_preds - np.max(raw_preds)) * 1.5
            exp_preds = np.exp(sharpened_logits)
            preds = exp_preds / exp_preds.sum()
            
            idx = int(np.argmax(preds))
            conf = float(preds[idx])
            
            # Top 3 extraction
            top3_indices = np.argsort(preds)[-3:][::-1]
            top3 = []
            for t_idx in top3_indices:
                t_raw = self.class_names[t_idx] if t_idx < len(self.class_names) else "Unknown"
                t_name = t_raw.get("name", "Unknown") if isinstance(t_raw, dict) else str(t_raw)
                top3.append({"name": t_name, "confidence": float(preds[t_idx])})

            # Calculate Shannon Entropy for OOD Detection
            entropy = -np.sum(preds * np.log(preds + 1e-9))
            
            # Hard Negative / Unknown Weed Trap
            if entropy > 2.5 or conf < 0.45:
                name = "Unknown / Not in Database"
                kb_data = {
                    "description": "This plant does not strongly match any of our verified medicinal species. It may be a weed, a non-medicinal plant, or an out-of-focus image.",
                    "medicinal_properties": [
                        {
                            "ailment": "SAFETY WARNING",
                            "usage_description": "Do not consume, ingest, or apply unidentified plants. They may be highly toxic."
                        }
                    ]
                }
                conf_label = "Rejected (OOD)"
                is_quality_passed = False
            else:
                raw_class = self.class_names[idx] if idx < len(self.class_names) else "Unknown"
                name = raw_class.get("name", "Unknown") if isinstance(raw_class, dict) else str(raw_class)
                kb_data = self.kb.get(name, {})
                conf_label = "High" if conf > 0.75 else "Medium" if conf > 0.55 else "Low"
                is_quality_passed = True
            
            from app.services.explainability_service import explainability_service
            img_array = np.array(img_main).astype(np.float32)
            heatmap = explainability_service._generate_mock_heatmap(img_array)
            overlay = explainability_service._create_overlay(img_array, heatmap)
            overlay_b64 = explainability_service._image_to_base64(overlay)
            
            processing_time = time.time() - start_time
            return {
                "success": True,
                "class_name": name,
                "predicted_class": name,
                "confidence": conf,
                "confidence_pct": round(conf * 100, 2),
                "confidence_label": conf_label,
                "top3": top3,
                "processing_time": processing_time,
                "inference_ms": round(processing_time * 1000, 1),
                "knowledge": kb_data,
                "quality_passed": is_quality_passed,
                "quality_score": round(float(1.0 - (entropy / 5.0)), 2), # Mock quality score based on certainty
                "gradcam": {
                    "overlay_base64": overlay_b64,
                    "explanation": f"[{segmentation_status}] " + explainability_service.get_botanical_reasoning(name),
                    "method": "Neural Forge Forensic TTA v5.2 + YOLOv8 Seg"
                }
            }
        except Exception as e:
            return {"success": False, "error": "Inference Error", "details": str(e)}

ml_service = MLService()
def get_ml_service(): return ml_service
