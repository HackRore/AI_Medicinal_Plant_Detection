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
    """Inference endpoint for raw image uploads."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Unsupported media type. Requires botanical image.")
    
    img_bytes = await file.read()
    return await execute_inference_pipeline(img_bytes, scale_reference)

@router.post("-url")
@limiter.limit("10/minute")
async def predict_url(request: Request, url: str = Form(...), scale_reference: bool = Form(False)):
    """Inference endpoint for remote URLs."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return await execute_inference_pipeline(resp.content, scale_reference)
    except Exception as e:
        logger.error(f"URL ingest failure: {str(e)}")
        raise HTTPException(400, "Failed to retrieve remote resource.")

async def execute_inference_pipeline(raw_image: bytes, scale_reference: bool):
    """Orchestrates multi-stage botanical verification and neural classification."""
    if len(raw_image) > 15 * 1024 * 1024:
        raise HTTPException(400, "Payload exceeds 15MB limit")

    # Concurrent gatekeeper and neural execution
    gatekeeper_task = asyncio.create_task(gemini_service.verify_is_leaf(raw_image))
    inference_payload = ml_service.predict(raw_image)

    try:
        gate_check = await asyncio.wait_for(gatekeeper_task, timeout=10.0)
        if not gate_check.get("is_leaf", True) and gate_check.get("confidence") == "high":
            return JSONResponse({
                "success": False,
                "error": "OOD_REJECTION",
                "message": gate_check.get("rejection_reason", "Non-botanical input"),
                "gatekeeper_meta": gate_check
            }, status_code=200)
    except asyncio.TimeoutError:
        logger.warning("Gatekeeper timeout; proceeding with neural inference")
    except Exception as e:
        logger.error(f"Gatekeeper exception: {str(e)}")

    if not inference_payload.get("success"):
        return JSONResponse(inference_payload, status_code=200)

    metadata = inference_payload.get("knowledge", {})
    taxon_id = inference_payload.get("class_name", "Unknown")
    common_name = metadata.get("common_names", [taxon_id])[0] if metadata.get("common_names") else taxon_id
    
    # Post-inference enrichment
    validation_task = asyncio.create_task(gemini_service.validate_prediction(common_name, raw_image))
    analysis_task = asyncio.create_task(gemini_service.get_plant_analysis(common_name, inference_payload.get("confidence_pct", 0), raw_image, scale_reference))
    
    response = {
        "success": True,
        "prediction_id": inference_payload.get("prediction_id"),
        "plant": {
            "name": common_name,
            "scientific_name": metadata.get("scientific_name", taxon_id),
            "family": metadata.get("family", "N/A"),
        },
        "prediction": {
            "confidence": inference_payload.get("confidence_pct", 0),
            "confidence_label": inference_payload.get("confidence_label", "Medium"),
            "top3": inference_payload.get("top3", []),
        },
        "medicinal": {
            "description": metadata.get("description", ""),
            "ayurvedic_uses": metadata.get("ayurvedic_uses", []),
        },
        "gradcam": inference_payload.get("gradcam", {}),
        "system_meta": {
            "latency_ms": inference_payload.get("inference_ms", 0),
            "engine": "plantoai_v3_core",
            "taxon_id": taxon_id
        }
    }

    try:
        vlm_analysis, cross_check = await asyncio.gather(
            asyncio.wait_for(analysis_task, timeout=20.0),
            asyncio.wait_for(validation_task, timeout=20.0),
            return_exceptions=True
        )
        if isinstance(vlm_analysis, dict) and "confirmed_name" in vlm_analysis:
            response["clinical_grounding"] = {
                "verdict": "Verified", 
                "observations": vlm_analysis.get("vision_note")
            }
        if isinstance(cross_check, dict):
            response["vision_validation"] = {
                "matches": cross_check.get("matches", True)
            }
    except Exception as e:
        logger.error(f"Enrichment task failure: {str(e)}")

    return response
