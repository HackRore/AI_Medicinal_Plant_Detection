from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.ml_service import ml_service
from app.services.gemini_service import gemini_service
from app.database import SessionLocal
from app.models.plant import Plant
import asyncio
import logging
import requests

logger = logging.getLogger(__name__)
router = APIRouter()
from app.limiter import limiter

@router.post("")
@limiter.limit("10/minute")
async def predict(request: Request, file: UploadFile = File(...), scale_reference: bool = Form(False)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid file type. Please upload a botanical image (JPG/PNG).")
    raw = await file.read()
    return await _process_prediction(raw, scale_reference)

@router.post("-url")
@limiter.limit("10/minute")
async def predict_url(request: Request, url: str = Form(...), scale_reference: bool = Form(False)):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return await _process_prediction(r.content, scale_reference)
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch image from URL: {e}")

async def _process_prediction(raw: bytes, scale_reference: bool):
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(400, "File too large. Maximum 15MB.")

    # Stage 2: Gemini Vision Pre-check
    leaf_check_task = asyncio.create_task(gemini_service.verify_is_leaf(raw))
    # Stage 3: Primary Neural Scan (ONNX)
    result = ml_service.predict(raw)

    try:
        leaf_check = await asyncio.wait_for(leaf_check_task, timeout=10.0)
        is_leaf = leaf_check.get("is_leaf", True)
        if not is_leaf and leaf_check.get("confidence") == "high":
            return JSONResponse({
                "success": False,
                "error": "Not a Plant Leaf",
                "message": leaf_check.get("rejection_reason", "Not a leaf."),
                "tips": ["Use a clear photo of a single leaf"],
                "stage2_check": leaf_check
            }, status_code=200)
    except:
        pass

    if not result.get("success"):
        return JSONResponse(result, status_code=200)

    # The 15% hard gate was removed to allow the Prototypical Engine (Phase 3)
    # to handle OOD detection and recovery more intelligently.
    kb = result.get("knowledge", {})

    # Safely get class_name from result
    class_name = result.get("class_name", "Unknown Plant")
    plant_name = kb.get("common_names", [class_name])[0] if kb.get("common_names") else class_name
    
    # Validation & Analysis
    validation_task = asyncio.create_task(gemini_service.validate_prediction(plant_name, raw))
    gemini_task = asyncio.create_task(gemini_service.get_plant_analysis(plant_name, result["confidence_pct"], raw, scale_reference))
    
    response = {
        "success": True,
        "prediction_id": result.get("prediction_id"),
        "plant": {
            "name": plant_name,
            "scientific_name": kb.get("scientific_name", result.get("class_name", "Unknown")),
            "family": kb.get("family", "N/A"),
        },
        "prediction": {
            "confidence": result.get("confidence_pct", 0),
            "confidence_label": result.get("confidence_label", "Medium"),
            "top3": result.get("top3", []),
        },
        "medicinal": {
            "description": kb.get("description", ""),
            "ayurvedic_uses": kb.get("ayurvedic_uses", []),
        },
        "gradcam": result.get("gradcam", {}),
        "quality": {"passed": result.get("quality_passed", True), "score": result.get("quality_score", 0.9)},
        "meta": {
            "inference_ms": result.get("inference_ms", 0),
            "model_version": "plantoai_v3_onnx_384px",
            "class_detected": result.get("class_name", "Unknown")
        }
    }

    try:
        gemini_data, validation_data = await asyncio.gather(
            asyncio.wait_for(gemini_task, timeout=25.0),
            asyncio.wait_for(validation_task, timeout=25.0),
            return_exceptions=True
        )
        if isinstance(gemini_data, dict) and "confirmed_name" in gemini_data:
            response["reasoning"] = {"verdict": "Verified", "analysis": gemini_data.get("vision_note")}
        if isinstance(validation_data, dict):
            response["vision_validation"] = {"matches_prediction": validation_data.get("matches", True)}
    except:
        pass

    return response
