from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import json
import time
import numpy as np
import onnxruntime as ort
from PIL import Image
import io
import logging
from typing import List, Dict, Any

from app.database import get_db
from app.models.prediction import Prediction
from app.models.plant import Plant

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Model Configuration ──────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../../ml_models")

# Priority order — use first one that exists
ONNX_MODEL_CANDIDATES = [
    os.path.join(MODEL_DIR, "efficientnetv2.onnx"),
    os.path.join(MODEL_DIR, "enhanced_model.onnx"),
    os.path.join(MODEL_DIR, "mobilenetv2_best.onnx"),
    os.path.join(MODEL_DIR, "vit_best.onnx"),
]

CONFIDENCE_THRESHOLD = 0.45
GAP_THRESHOLD = 0.05
INPUT_SIZE = 224  # standard for EfficientNet and MobileNet

# ── Load Model & Class Names ─────────────────────────────────────
session = None
class_names = []
model_input_name = None

def load_model():
    global session, class_names, model_input_name

    # Load class names
    try:
        class_path = os.path.join(MODEL_DIR, "class_names.json")
        with open(class_path) as f:
            class_names = json.load(f)
        logger.info(f"Loaded {len(class_names)} class names")
    except Exception as e:
        logger.error(f"Class names load error: {e}")
        class_names = []

    # Load ONNX model
    for model_path in ONNX_MODEL_CANDIDATES:
        if os.path.exists(model_path):
            try:
                session = ort.InferenceSession(
                    model_path,
                    providers=["CPUExecutionProvider"]
                )
                model_input_name = session.get_inputs()[0].name
                size_mb = os.path.getsize(model_path) / (1024 * 1024)
                logger.info(f"ONNX model loaded: {os.path.basename(model_path)} ({size_mb:.1f} MB)")
                return True
            except Exception as e:
                logger.error(f"Failed to load {model_path}: {e}")
                continue

    logger.warning("WARNING: No ONNX model loaded")
    return False

load_model()

# ── Preprocessing ────────────────────────────────────────────────
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Preprocess image for model inference."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((INPUT_SIZE, INPUT_SIZE), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    # Normalize with ImageNet mean/std
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    arr = (arr - mean) / std
    return np.expand_dims(arr, axis=0).astype(np.float32)

# ── Inference ────────────────────────────────────────────────────
def run_inference(image_bytes: bytes) -> dict:
    """Run ONNX inference. Returns prediction dict."""
    if session is None:
        if not load_model():
            return {"success": False, "message": "Model not loaded. Try again in 30 seconds."}
    if not class_names:
        return {"success": False, "message": "Class names not loaded."}

    try:
        start = time.time()
        img_array = preprocess_image(image_bytes)
        outputs = session.run(None, {model_input_name: img_array})
        raw_preds = outputs[0][0]

        # Softmax
        exp_preds = np.exp(raw_preds - np.max(raw_preds))
        predictions = exp_preds / exp_preds.sum()

        # Top 3
        top_indices = np.argsort(predictions)[-3:][::-1]
        top_predictions = [
            {
                "rank": i + 1,
                "plant": class_names[idx],
                "confidence": round(float(predictions[idx]) * 100, 1)
            }
            for i, idx in enumerate(top_indices)
            if idx < len(class_names)
        ]

        best_idx = top_indices[0]
        best_conf = float(predictions[best_idx])
        best_name = class_names[best_idx]

        inference_time = round((time.time() - start) * 1000, 1)
        logger.info(f"Inference: {best_name} ({best_conf*100:.1f}%) in {inference_time}ms")

        # Confidence check
        if best_conf < CONFIDENCE_THRESHOLD:
            return {
                "success": False,
                "identified": False,
                "message": f"Image unclear or plant not in database. Best guess: {best_name} ({best_conf*100:.0f}%). Try a clearer, well-lit photo.",
                "top_predictions": top_predictions,
                "inference_time_ms": inference_time,
                "plant_name": best_name,
                "confidence": round(best_conf * 100, 1)
            }

        return {
            "success": True,
            "identified": True,
            "plant_name": best_name,
            "confidence": round(best_conf * 100, 1),
            "top_predictions": top_predictions,
            "inference_time_ms": inference_time
        }

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return {"success": False, "message": f"Prediction failed: {str(e)[:100]}"}

# ── Predict Endpoint ─────────────────────────────────────────────
@router.post("")
async def predict_plant(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Main prediction endpoint."""
    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
            
        image_bytes = await file.read()
        total_start = time.time()
        
        if len(image_bytes) == 0:
            return {"success": False, "message": "Empty file uploaded"}
        if len(image_bytes) > 10 * 1024 * 1024:
            return {"success": False, "message": "File too large. Max 10MB."}

        # Run ONNX inference
        result = run_inference(image_bytes)
        if not result.get("success") and not result.get("plant_name"):
            return result

        plant_name = result["plant_name"]
        confidence = result["confidence"] / 100

        # Phase 3: Gemini Ayurvedic Enrichment
        from app.services.gemini_service import get_plant_analysis
        gemini_data = {}
        try:
            gemini_data = await get_plant_analysis(
                plant_name=plant_name,
                confidence=confidence,
                image_bytes=image_bytes
            )
        except Exception as e:
            logger.warning(f"Gemini enrichment failed: {e}")

        # Get DB data
        plant = db.query(Plant).filter(Plant.species_name == plant_name).first()
        
        total_time = time.time() - total_start
        
        # Save to DB
        prediction_record = Prediction(
            image_url="processed",
            predicted_plant_id=plant.id if plant else None,
            confidence_score=confidence,
            model_version="ONNX_V1",
            processing_time_ms=total_time * 1000
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        return {
            "success": True,
            "identified": result.get("identified", False),
            "prediction_id": prediction_record.id,
            "plant_name": plant_name,
            "confidence": result["confidence"],
            "top_predictions": result["top_predictions"],
            "inference_time_ms": result["inference_time_ms"],
            "ai_debate": gemini_data,
            "plant_details": {
                "common_name": plant.common_name_en if plant else None,
                "description": plant.description if plant else None,
                "scientific_name": plant.species_name if plant else plant_name
            } if plant else None
        }

    except HTTPException: raise
    except Exception as e:
        logger.error(f"Critical prediction failure: {e}")
        return {
            "success": False,
            "message": "Unexpected error. Please try again.",
            "error": str(e)[:100]
        }

@router.get("/history")
async def get_prediction_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    try:
        predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
        results = []
        for pred in predictions:
            plant = db.query(Plant).filter(Plant.id == pred.predicted_plant_id).first()
            results.append({
                "id": pred.id,
                "image_url": pred.image_url,
                "predicted_plant": plant.species_name if plant else "Unknown",
                "common_name": plant.common_name_en if plant else None,
                "confidence": pred.confidence_score,
                "created_at": pred.created_at.isoformat() if pred.created_at else None,
                "feedback_correct": pred.feedback_correct
            })
        return {"total": db.query(Prediction).count(), "skip": skip, "limit": limit, "predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@router.post("/{prediction_id}/feedback")
async def submit_feedback(
    prediction_id: int,
    correct: bool,
    comment: str = None,
    db: Session = Depends(get_db)
):
    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not prediction: raise HTTPException(status_code=404, detail="Prediction not found")
        prediction.feedback_correct = correct
        prediction.feedback_comment = comment
        db.commit()
        return {"message": "Feedback submitted successfully", "prediction_id": prediction_id}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")
