import onnxruntime as ort
import numpy as np
import cv2
import base64
import json
import time
import os
import logging
from io import BytesIO
import tempfile
from botanical_gate import gate
from prototypical_inference import PrototypicalClassifier

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
    # Using the fine-tuned leaf detector, falling back to standard if not ready
    YOLO_MODEL_PATH_LEAF = os.path.join(_BACKEND, 'ml_models', 'yolov8n_leaf.pt')
    YOLO_MODEL_PATH_GENERIC = os.path.join(_BACKEND, 'ml_models', 'yolov8n.pt')
    
    if os.path.exists(YOLO_MODEL_PATH_LEAF):
        leaf_detector = YOLO(YOLO_MODEL_PATH_LEAF)
        logger.info("YOLOv8 Fine-Tuned Leaf Segmentation Engine: ONLINE")
    else:
        leaf_detector = YOLO(YOLO_MODEL_PATH_GENERIC if os.path.exists(YOLO_MODEL_PATH_GENERIC) else 'yolov8n.pt')
        logger.info("YOLOv8 Generic Segmentation Engine: ONLINE")
    
    YOLO_AVAILABLE = True
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

MODEL_PATH = _find('plantoai_v3.onnx', ['ml_models'])
CLASS_PATH = _find('class_names.json',    ['app/data'])
KB_PATH    = _find('medicinal_knowledge.json', ['app/data'])

class MLService:
    """Orchestrates neural inference and knowledge base mapping."""
    def __init__(self):
        self.config = ModelConfig()
        self.engine = PrototypicalEngine(self.config)
        self.session = None
        
        try:
            # CPU-optimized execution provider for containerized environments
            options = ort.SessionOptions()
            options.intra_op_num_threads = 1
            options.inter_op_num_threads = 1
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            self.session = ort.InferenceSession(
                self.config.ONNX_MODEL, 
                sess_options=options,
                providers=['CPUExecutionProvider']
            )
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
            
            # --- Phase 1: BioCLIP 2 Botanical Gatekeeper ---
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            gate_result = gate.verify(tmp_path)
            if not gate_result.get("is_leaf", True):
                return {
                    "status": "rejected",
                    "success": False,
                    "error": "Invalid Bio-Signature Detected",
                    "message": gate_result.get("reason", "Not a leaf."),
                    "botanical_confidence": round(gate_result.get("confidence", 0) * 100, 2),
                    "species": None
                }

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
            img_main = img.resize((384, 384))
            
            def preprocess(i):
                x = np.array(i.resize((384, 384))).astype(np.float32) / 255.0
                # ImageNet Normalization (CRITICAL for EfficientNetV2)
                mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
                std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
                x = (x - mean) / std
                return np.transpose(x, (2, 0, 1)).reshape(1, 3, 384, 384)

            input_name = self.sess.get_inputs()[0].name
            
            # --- TTA PASSES ---
            passes = []
            # 1. Original
            passes.append(img_main)
            # 2. Horizontal Flip
            passes.append(img_main.transpose(Image.FLIP_LEFT_RIGHT))
            # 3. +10 rotation
            passes.append(img_main.rotate(10))
            # 4. -10 rotation
            passes.append(img_main.rotate(-10))
            # 5. Center crop 90%
            w, h = img_main.size
            cw, ch = int(w * 0.9), int(h * 0.9)
            passes.append(img_main.crop(((w-cw)//2, (h-ch)//2, w-(w-cw)//2, h-(h-ch)//2)).resize((384, 384)))
            
            all_preds = []
            for p_img in passes:
                input_tensor = preprocess(p_img)
                outputs = self.sess.run(None, {input_name: input_tensor})
                raw_preds = outputs[0][0]
                exp_preds = np.exp(raw_preds - np.max(raw_preds))
                all_preds.append(exp_preds / exp_preds.sum())
            
            preds = np.mean(all_preds, axis=0)
            
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
            
            # Always resolve the top predicted class first
            raw_class = self.class_names[idx] if idx < len(self.class_names) else "Unknown"
            name = raw_class.get("name", "Unknown") if isinstance(raw_class, dict) else str(raw_class)
            kb_data = self.kb.get(name, {})
            
            # OOD Gate: only reject if genuinely ambiguous (very high entropy AND very low confidence)
            # Thresholds are deliberately lenient to avoid rejecting real leaf photos
            if entropy > 3.8 and conf < 0.12:
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
                conf_label = "High" if conf > 0.75 else "Medium" if conf > 0.45 else "Low"
                is_quality_passed = conf > 0.30

            # --- Phase 3: Prototypical Path ---
            proto_result = self.proto_engine.predict(gate.get_bioclip_embedding(tmp_path))
            proto_top1 = proto_result.get("top1_species", "Unknown")
            proto_conf = proto_result.get("top1_confidence", 0)
            
            # --- Decision Combination (Ensemble) ---
            onnx_top1 = name
            final_confidence = conf
            final_tier = conf_label
            is_ambiguous = proto_result.get("ambiguous", False)
            
            # ENSEMBLE DECISION: Sharp Boundaries Logic (Phase 3)
            # Trust the Prototypical Engine if it's more confident than ONNX, or if ONNX is weak
            if proto_conf > conf or (conf < 0.30 or entropy > 3.2):
                logger.info(f"Neural Shift: Prioritizing Prototypical Engine ({proto_top1}) [Conf: {proto_conf:.2f}] over ONNX ({onnx_top1}) [Conf: {conf:.2f}]")
                name = proto_top1
                final_confidence = proto_conf
                final_tier = proto_result.get("confidence_tier")
                is_quality_passed = proto_conf > 0.40
            else:
                # Trust ONNX but calibrate with Proto
                name = onnx_top1
                final_confidence = conf
                final_tier = conf_label
                is_quality_passed = conf > 0.30

            # Conflict Detection
            if onnx_top1 != proto_top1 and proto_conf > 0.50:
                is_ambiguous = True
                final_tier = "AMBIGUOUS — Cross-verification required"

            from app.services.explainability_service import explainability_service
            img_array = np.array(img_main).astype(np.float32)
            heatmap = explainability_service._generate_mock_heatmap(img_array)
            overlay = explainability_service._create_overlay(img_array, heatmap)
            overlay_b64 = explainability_service._image_to_base64(overlay)
            
            processing_time = time.time() - start_time
            
            # --- Phase 4: Persistent Memory (Log Prediction) ---
            from app.services.feedback_service import feedback_service
            import hashlib
            img_hash = hashlib.md5(image_bytes).hexdigest()
            prediction_id = feedback_service.log_prediction(
                image_hash=img_hash,
                predicted_species=name,
                confidence=float(final_confidence),
                gate_score=round(float(1.0 - (entropy / 5.0)), 2),
                meta={"model": "plantoai_v3_onnx_384px", "ensemble": "prototypical"}
            )

            return {
                "success": True,
                "prediction_id": prediction_id,

                "class_name": name,
                "predicted_class": name,
                "confidence": float(final_confidence),
                "confidence_pct": round(float(final_confidence) * 100, 2),
                "confidence_label": final_tier,
                "confidence_tier": final_tier,
                "top3": top3,
                "proto_top3": proto_result.get("top3", []),
                "ambiguous": is_ambiguous,
                "processing_time": processing_time,
                "inference_ms": round(processing_time * 1000, 1),
                "knowledge": kb_data,
                "quality_passed": is_quality_passed,
                "quality_score": round(float(1.0 - (entropy / 5.0)), 2),
                "gradcam": {
                    "overlay_base64": overlay_b64,
                    "explanation": f"[{segmentation_status}] " + explainability_service.get_botanical_reasoning(name),
                    "method": "Neural Forge v5.5 (TTA + Prototypical Calibration)"
                }
            }
        except Exception as e:
            logger.error(f"Inference critical failure: {e}")
            return {"success": False, "error": "Inference Error", "details": str(e)}
        finally:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

ml_service = MLService()
def get_ml_service(): return ml_service
