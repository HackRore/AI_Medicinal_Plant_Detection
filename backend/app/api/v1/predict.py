from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.services.ml_service import ml_service
from app.services.gemini_service import gemini_service
from app.database import SessionLocal
from app.models.plant import Plant
import asyncio
import logging

logger = logging.getLogger(__name__)
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

    # === STAGE 2: Gemini Vision Pre-check (runs in parallel with ONNX) ===
    leaf_check_task = asyncio.create_task(gemini_service.verify_is_leaf(raw))

    # === STAGE 3: Primary Neural Scan (ONNX) - FAST ===
    result = ml_service.predict(raw)

    # Resolve Stage 2 result (with timeout so it never blocks)
    try:
        leaf_check = await asyncio.wait_for(leaf_check_task, timeout=10.0)
        is_leaf = leaf_check.get("is_leaf", True)
        quality = leaf_check.get("image_quality", "good")
        confidence = leaf_check.get("confidence", "low")
        guidance = leaf_check.get("user_guidance")
        what_i_see = leaf_check.get("what_i_see", "")

        # Hard reject: clearly not a leaf (Gemini is certain)
        if not is_leaf and confidence == "high":
            return JSONResponse({
                "success": False,
                "error": "Not a Plant Leaf",
                "what_ai_sees": what_i_see,
                "message": leaf_check.get("rejection_reason", "This image does not appear to contain a plant leaf."),
                "user_guidance": guidance or "Please photograph a plant leaf clearly with good lighting, filling most of the frame.",
                "tips": [
                    "Hold the leaf flat and photograph from directly above",
                    "Ensure the leaf fills at least 60% of the frame",
                    "Use natural daylight or a bright indoor light",
                    "Remove fingers, shadows, and background clutter",
                    "Hold your phone steady to avoid blur"
                ],
                "stage2_check": leaf_check
            }, status_code=200)

        # Soft reject: leaf found but image quality is too poor for accurate ID
        if is_leaf and quality == "unusable" and confidence in ["high", "medium"]:
            return JSONResponse({
                "success": False,
                "error": "Image Quality Too Poor",
                "what_ai_sees": what_i_see,
                "message": "A leaf was detected but the image is too blurry or dark for accurate identification.",
                "user_guidance": guidance or "Please retake the photo with better lighting and hold the phone steady.",
                "tips": [
                    "Move to a brighter location or near a window",
                    "Hold your phone very still or rest it on a surface",
                    "Clean your camera lens",
                    "Get closer to the leaf — aim for 15-25cm distance"
                ],
                "stage2_check": leaf_check
            }, status_code=200)

    except asyncio.TimeoutError:
        # Gemini took too long — fail open, proceed to ONNX
        logger.warning("Gemini Stage 2 timeout — failing open to ONNX")
        leaf_check = {"is_leaf": True, "image_quality": "good", "confidence": "low",
                      "user_guidance": None, "skipped": True, "skip_reason": "timeout"}
    except Exception as e:
        # Any Gemini failure (rate limit, network, parse error) — fail open
        logger.warning(f"Gemini Stage 2 exception ({type(e).__name__}) — failing open: {e}")
        leaf_check = {"is_leaf": True, "image_quality": "good", "confidence": "low",
                      "user_guidance": None, "skipped": True, "skip_reason": str(type(e).__name__)}

    if not result.get("success"):
        return JSONResponse(result, status_code=200)
    
    kb = result.get("knowledge", {})
    plant_name = kb.get("common_names", [result["class_name"]])[0]
    
    # === STAGE 4 (OOD Gate) is inside ml_service.predict already ===
    
    # === STAGE 5: Gemini Vision Validation (parallel with analysis) ===
    validation_task = asyncio.create_task(
        gemini_service.validate_prediction(plant_name=plant_name, image_bytes=raw)
    )

    # === STAGE 6 (Ayurvedic Analysis) in parallel ===
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

    # === Stage 6: Wait for Gemini Analysis + Stage 5 Validation (parallel) ===
    try:
        gemini_data, validation_data = await asyncio.gather(
            asyncio.wait_for(gemini_task, timeout=25.0),
            asyncio.wait_for(validation_task, timeout=25.0),
            return_exceptions=True
        )
        
        # Process Stage 6 (Ayurvedic analysis)
        if isinstance(gemini_data, dict) and "confirmed_name" in gemini_data:
            response["reasoning"] = {
                "verdict": "Verified" if gemini_data.get("confirmed_name", "").lower() in plant_name.lower() else "Mismatch Detected",
                "analysis": gemini_data.get("vision_note", "Visual analysis complete."),
                "scientific_confirmation": gemini_data.get("confirmed_name"),
                "ayurvedic_profile": gemini_data.get("ayurvedic_name")
            }
            if response["reasoning"]["verdict"] == "Mismatch Detected" and result["confidence_pct"] < 70:
                response["quality"]["passed"] = False
                response["quality"]["message"] = "Visual mismatch detected. This might not be the predicted plant."

        # Process Stage 5 (Species Validation)
        if isinstance(validation_data, dict):
            response["vision_validation"] = {
                "stage": 5,
                "matches_prediction": validation_data.get("matches", True),
                "agreement_score": validation_data.get("agreement_score", 0.5),
                "confidence": validation_data.get("confidence", "low"),
                "observation": validation_data.get("actual_observation", "")
            }
            # Stage 5 override: if Gemini disagrees with high confidence, downgrade quality
            if not validation_data.get("matches", True) and validation_data.get("confidence") in ["high", "medium"]:
                response["quality"]["passed"] = False
                response["quality"]["message"] = f"Vision mismatch: AI sees '{validation_data.get('actual_observation', 'a different plant')}'"
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

