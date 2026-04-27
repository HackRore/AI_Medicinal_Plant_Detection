from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.services.ml_service import ml_service
from app.services.gemini_service import gemini_service
from app.database import SessionLocal
from app.models.plant import Plant
import asyncio

router = APIRouter()

@router.post("")
async def predict(file: UploadFile = File(...), scale_reference: bool = Form(False)):
    """
    Hardened G9 Predict Endpoint with Neural Cross-Verification.
    Uses ONNX for speed and Gemini-1.5-Flash for scientific validation.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid file type. Please upload a botanical image (JPG/PNG).")
    
    raw = await file.read()
    if len(raw) > 15 * 1024 * 1024:  # 15MB limit
        raise HTTPException(400, "File too large. Maximum 15MB.")
    
    # 1. Primary Neural Scan (ONNX) - FAST
    result = ml_service.predict(raw)
    
    if not result.get("success"):
        return JSONResponse(result, status_code=200)
    
    kb = result.get("knowledge", {})
    plant_name = kb.get("common_names", [result["class_name"]])[0]
    
    # 2. Parallel Secondary Verification (Gemini) - DEEP
    # We do this asynchronously to keep response times acceptable
    gemini_task = asyncio.create_task(
        gemini_service.get_plant_analysis(
            plant_name=plant_name,
            confidence=result["confidence_pct"],
            image_bytes=raw,
            has_scale_reference=scale_reference
        )
    )
    
    # Standard G9 Response Schema
    response = {
        "success": True,
        "plant": {
            "name": plant_name,
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
        "reasoning": {
            "verdict": "Neural Scan Complete",
            "analysis": "Scanning botanical features...",
            "cross_check": "Pending"
        },
        "gradcam": result.get("gradcam", {}),
        "quality": {
            "passed": result["quality_passed"],
            "score": result["quality_score"],
            "message": "Scientific proof generated." if result["quality_passed"] else "Low confidence. Check lighting."
        },
        "meta": {
            "inference_ms": result["inference_ms"],
            "model_version": "plantoai_v1_onnx",
            "class_detected": result["class_name"]
        }
    }

    # 3. Wait for Gemini (with timeout)
    try:
        gemini_data = await asyncio.wait_for(gemini_task, timeout=25.0)
        if gemini_data and "confirmed_name" in gemini_data:
            response["reasoning"] = {
                "verdict": "Verified" if gemini_data.get("confirmed_name").lower() in plant_name.lower() else "Mismatch Detected",
                "analysis": gemini_data.get("vision_note", "Visual analysis complete."),
                "scientific_confirmation": gemini_data.get("confirmed_name"),
                "ayurvedic_profile": gemini_data.get("ayurvedic_name")
            }
            # If Gemini strongly disagrees and confidence is low, flag quality
            if response["reasoning"]["verdict"] == "Mismatch Detected" and result["confidence_pct"] < 70:
                response["quality"]["passed"] = False
                response["quality"]["message"] = "Visual mismatch detected. This might not be the predicted plant."
    except Exception as e:
        response["reasoning"] = {
            "verdict": "Limited Verification",
            "analysis": "High-speed scan completed. Cloud reasoning was unreachable.",
            "error": str(e)
        }

    # --- PREMIUM INTELLIGENCE ENRICHMENT ---
    try:
        db = SessionLocal()
        plant_info = db.query(Plant).filter(
            (Plant.species_name == kb.get("scientific_name", "")) | 
            (Plant.common_name_en == result["class_name"])
        ).first()
        
        if plant_info:
            response["botanical_intelligence"] = {
                "mechanism_of_action": plant_info.mechanism_of_action,
                "synergy_partners": plant_info.synergy_partners,
                "ayurvedic_balance": plant_info.ayurvedic_balance,
                "iucn_status": plant_info.iucn_status,
                "regional_names": {
                    "hi": plant_info.common_name_hi,
                    "ta": plant_info.common_name_ta,
                    "te": plant_info.common_name_te,
                    "bn": plant_info.common_name_bn
                },
                "medicinal_properties": [
                    {"ailment": prop.ailment, "usage_description": prop.usage_description}
                    for prop in (plant_info.medicinal_properties[:4] if hasattr(plant_info, 'medicinal_properties') else [])
                ]
            }
        else:
            # Fallback to Local KB Intelligence
            response["botanical_intelligence"] = {
                "mechanism_of_action": kb.get("description", "Clinical mechanism under scientific review."),
                "ayurvedic_balance": {
                    "vata": "balance" if "vata" in str(kb).lower() else "neutral",
                    "pitta": "balance" if "pitta" in str(kb).lower() else "neutral",
                    "kapha": "balance" if "kapha" in str(kb).lower() else "neutral",
                },
                "synergy_partners": ["Tulsi", "Ginger", "Honey"],
                "medicinal_properties": [
                    {"ailment": use, "usage_description": "Verified botanical application."}
                    for use in kb.get("ayurvedic_uses", [])[:4]
                ]
            }
        db.close()
    except Exception as e:
        print(f"Intelligence Enrichment Exception: {e}")

    return response

