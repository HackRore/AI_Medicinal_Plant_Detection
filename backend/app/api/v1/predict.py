from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import json
import time
import numpy as np
from PIL import Image
import io
import logging
from typing import List, Dict, Any

from app.database import get_db
from app.models.prediction import Prediction
from app.models.plant import Plant

# Configure logging
logger = logging.getLogger(__name__)
router = APIRouter()

# ── Step 4: TensorFlow with graceful fallback ─────────────────────
try:
    import tensorflow as tf
    TF_AVAILABLE = True
    print("TensorFlow loaded successfully")
except ImportError:
    TF_AVAILABLE = False
    print("WARNING: TensorFlow not available")

# ONNX Runtime fallback
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
    print("ONNX Runtime loaded successfully")
except ImportError:
    ONNX_AVAILABLE = False
    print("WARNING: ONNX Runtime not available")

# ── Global State ──────────────────────────────────────────────────
model = None  # TensorFlow model
session = None # ONNX session
class_names = []
model_type = None # "TF" or "ONNX"

def load_model():
    global model, session, class_names, model_type
    try:
        # 1. Load class names
        class_names_path = os.path.join(
            os.path.dirname(__file__),
            "../../../ml_models/class_names.json"
        )
        if os.path.exists(class_names_path):
            with open(class_names_path) as f:
                class_names = json.load(f)
            print(f"Loaded {len(class_names)} class names")
        else:
            print("WARNING: class_names.json not found")

        # 2. Try TensorFlow model first (as requested)
        if TF_AVAILABLE:
            model_path = os.path.join(
                os.path.dirname(__file__),
                "../../../ml_models/efficientnetv2_best.h5"
            )
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path, compile=False)
                model_type = "TF"
                print("TensorFlow model loaded successfully")
                return True

        # 3. Fallback to ONNX Runtime
        if ONNX_AVAILABLE:
            onnx_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../ml_models/efficientnetv2.onnx"
            )
            if os.path.exists(onnx_path):
                session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
                model_type = "ONNX"
                print(f"ONNX model loaded successfully from {onnx_path}")
                return True

        print("Model not loaded — predictions will use fallback")
        return False
    except Exception as e:
        print(f"Model load error: {e}")
        return False

# Load on startup
load_model()

# ── Preprocessing ────────────────────────────────────────────────
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Preprocess image for model inference (224x224)."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    
    # ImageNet normalization
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    arr = (arr - mean) / std
    
    return np.expand_dims(arr, axis=0).astype(np.float32)

# ── Predict Endpoint ─────────────────────────────────────────────
@router.post("")
async def predict_plant(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Main prediction endpoint with safety check."""
    # Step 4: Safety Check
    if model is None and session is None:
        return {
            "success": False,
            "message": "AI model is loading or unavailable. Please try again in 30 seconds.",
            "error": "model_not_loaded"
        }

    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
            
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            return {"success": False, "message": "Empty file uploaded"}
        
        start_time = time.time()
        processed_img = preprocess_image(image_bytes)

        # Inference based on loaded type
        if model_type == "TF" and model:
            preds = model.predict(processed_img, verbose=0)[0]
        elif model_type == "ONNX" and session:
            input_name = session.get_inputs()[0].name
            outputs = session.run(None, {input_name: processed_img})
            raw_preds = outputs[0][0]
            # Softmax
            exp_preds = np.exp(raw_preds - np.max(raw_preds))
            preds = exp_preds / exp_preds.sum()
        else:
            return {"success": False, "message": "Inference engine mismatch"}

        # Process results
        top_indices = np.argsort(preds)[-3:][::-1]
        best_idx = int(top_indices[0])
        confidence = float(preds[best_idx])
        plant_name = class_names[best_idx] if best_idx < len(class_names) else "Unknown"

        top_predictions = [
            {
                "plant": class_names[idx] if idx < len(class_names) else f"Unknown_{idx}",
                "confidence": round(float(preds[idx]) * 100, 1)
            }
            for idx in top_indices
        ]

        # Get Gemini Ayurvedic Enrichment
        from app.services.gemini_service import get_plant_analysis
        gemini_data = await get_plant_analysis(
            plant_name=plant_name,
            confidence=confidence,
            image_bytes=image_bytes
        )

        # Database lookup
        plant = db.query(Plant).filter(Plant.species_name == plant_name).first()
        
        # Save Prediction Record
        total_time = (time.time() - start_time) * 1000
        prediction_record = Prediction(
            image_url="processed",
            predicted_plant_id=plant.id if plant else None,
            confidence_score=confidence,
            model_version=f"{model_type}_V2",
            processing_time_ms=total_time
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        return {
            "success": True,
            "prediction_id": prediction_record.id,
            "plant_name": plant_name,
            "confidence": round(confidence * 100, 1),
            "top_predictions": top_predictions,
            "inference_time_ms": round(total_time, 1),
            "ai_debate": gemini_data,
            "plant_details": {
                "common_name": plant.common_name_en if plant else None,
                "description": plant.description if plant else None,
                "scientific_name": plant.species_name if plant else plant_name
            } if plant else None
        }

    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        return {
            "success": False,
            "message": "Internal processing error",
            "error": str(e)
        }

# Maintain legacy route if needed (aliased to predict_plant)
@router.post("/predict")
async def predict_alias(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await predict_plant(file, db)
