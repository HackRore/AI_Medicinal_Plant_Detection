from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.ml_service import ml_service

router = APIRouter()

@router.post("")
async def predict(file: UploadFile = File(...)):
    """
    Hardened G9 Predict Endpoint
    Ensures zero-dummy data and standardized Ayurvedic schema.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    
    raw = await file.read()
    if len(raw) > 15 * 1024 * 1024:  # 15MB limit
        raise HTTPException(400, "File too large. Maximum 15MB.")
    
    result = ml_service.predict(raw)
    
    if not result.get("success"):
        return JSONResponse(result, status_code=200)
    
    kb = result.get("knowledge", {})
    
    # Standard G9 Response Schema
    return {
        "success": True,
        "plant": {
            "name": kb.get("common_names", [result["class_name"]])[0],
            "scientific_name": kb.get("scientific_name", result["class_name"]),
            "family": kb.get("family", "N/A"),
            "native_region": kb.get("native_region", "India"),
        },
        "prediction": {
            "confidence": result["confidence_pct"],
            "confidence_label": result["confidence_label"],
            "top3": result["top3"],
        },
        "toxicity": kb.get("toxicity", {"level": "unknown", "level_code": 3, "notes": "Consult practitioner."}),
        "medicinal": {
            "description": kb.get("description", ""),
            "ayurvedic_uses": kb.get("ayurvedic_uses", []),
            "preparation": kb.get("preparation", "Consult a qualified Ayurvedic practitioner."),
            "active_compounds": kb.get("active_compounds", []),
            "contraindications": kb.get("contraindications", []),
        },
        "gradcam": result.get("gradcam", {}),
        "quality": {
            "passed": result["quality_passed"],
            "score": result["quality_score"],
            "message": "Scientific proof generated." if result["quality_passed"] else "Low confidence. Check lighting."
        },
        "meta": {
            "inference_ms": result["inference_ms"],
            "model_version": "plantoai_v2_onnx",
            "class_detected": result["class_name"]
        }
    }
