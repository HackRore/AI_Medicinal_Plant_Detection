"""
Prediction API Routes
Plant identification from leaf images
"""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import time
import os
from datetime import datetime
from PIL import Image
import io
import logging
import uuid

from app.database import get_db
from app.services.ml_service import get_ml_service
from app.services.gemini_service import get_gemini_service
from app.models.prediction import Prediction
from app.models.plant import Plant
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("")
async def predict_plant(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a leaf image and get plant identification prediction
    
    - **file**: Image file (JPEG/PNG)
    - Returns: Predicted plant species, confidence score, and details
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file size
        if len(image_bytes) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Get ML service and make prediction
        ml_service = get_ml_service()
        start_time = time.time()
        prediction_result = ml_service.predict(image_bytes)
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # --- PRO-GRADE INTELLIGENT STORAGE FILTER ---
        # We don't save the file yet. We analyze it in-memory first.
        
        CONFIDENCE_THRESHOLD = 0.45
        GAP_THRESHOLD = 0.05
        
        predicted_class = prediction_result["predicted_class"]
        confidence = prediction_result["confidence"]
        top_predictions = prediction_result.get("top_predictions", [])
        
        # Calculate gap between top 1 and top 2
        gap = 1.0  # Default if only one class exists
        if len(top_predictions) >= 2:
            gap = top_predictions[0]["confidence"] - top_predictions[1]["confidence"]
        
        gate = prediction_result.get("gate") or {}
        gate_enabled = bool(gate.get("enabled"))
        gate_is_leaf = gate.get("is_leaf")

        # If gate is confident:
        # - leaf => show plant details and (optionally) save
        # - non_leaf => reject early
        if gate_enabled and gate_is_leaf is True:
            is_robust = True
        elif gate_enabled and gate_is_leaf is False:
            is_robust = False
        else:
            is_robust = confidence >= CONFIDENCE_THRESHOLD and gap >= GAP_THRESHOLD
        
        # Determine if we should save this data for future training
        # ONLY save if it is likely a medicinal plant to keep the dataset "pure"
        filepath = None
        prediction_id = None
        plant = None
        
        # Never save if leaf-gate rejected (not a leaf)
        if prediction_result.get("predicted_class_index") == -1 and predicted_class == "Not a Plant Leaf":
            is_robust = False

        if not is_robust:
             # Low confidence or ambiguous - we still keep the original class name for now
             # but we log it
             logger.info(f"🛡️ Storage Filter: Signal non-leaf/ambiguous image (Conf: {confidence:.2f}). No file saved.")
        else:
            # Valid image! Save to disk and DB for the "Continuous Learning Loop"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = f"{timestamp}_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(settings.UPLOAD_DIR, safe_name)
            
            # --- PRIVACY GUARD: STRIP EXIF DATA ---
            try:
                img = Image.open(io.BytesIO(image_bytes))
                # Re-saving as RGB strips all metadata/EXIF by default in PIL
                img.save(filepath, format="JPEG", quality=95, optimize=True)
                logger.info(f"🛡️ Privacy Guard: Stripped EXIF data from {filename}")
            except Exception as e:
                logger.warning(f"⚠️ Privacy Guard failed: {e}. Falling back to raw save.")
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
            
            plant = db.query(Plant).filter(
                Plant.species_name == predicted_class
            ).first()
            
            # Store prediction in database
            prediction_record = Prediction(
                image_url=filepath,
                predicted_plant_id=plant.id if plant else None,
                confidence_score=prediction_result["confidence"],
                model_version=prediction_result["model_version"],
                ensemble_used=prediction_result["ensemble_used"],
                processing_time_ms=processing_time
            )
            db.add(prediction_record)
            db.commit()
            db.refresh(prediction_record)
            prediction_id = prediction_record.id
            logger.info(f"✅ Storage Filter: Accepted leaf image for {predicted_class}. Saved to {filepath}")
        
        # Prepare response
        response = {
            "prediction_id": prediction_id,
            "predicted_class": predicted_class,
            "predicted_class_index": prediction_result.get("predicted_class_index"),
            "confidence": prediction_result["confidence"],
            "top_predictions": prediction_result["top_predictions"],
            "processing_time_ms": processing_time,
            "model_version": prediction_result["model_version"],
            "plant_details": None,
            "expert_verification": None,
            "storage_status": "saved" if prediction_id else "filtered_out",
            "gate": prediction_result.get("gate"),
            "message": prediction_result.get("message"),
            "gradcam_base64": prediction_result.get("gradcam_base64"),
            "medicinal_info": prediction_result.get("medicinal_info"),
            "alternatives": prediction_result.get("top_predictions", []),
            "is_toxic": prediction_result.get("is_toxic", False),
            "caution": prediction_result.get("caution", "")
        }
        
        # Expert Fallback Logic - HIGH Intelligence mode
        # Trigger Gemini if:
        # 1. Local confidence is < 95% (Raised from 85%)
        # 2. Rejection logic flagged it as not robust
        try:
            if not is_robust or confidence < 0.95:
                gemini = get_gemini_service()
                response["gemini_initialized"] = gemini.initialized
                if gemini.initialized:
                    expert_result = await gemini.identify_plant_from_image(image_bytes)
                    if expert_result:
                        response["expert_verification"] = expert_result
                        response["expert_verification_status"] = "success"
                        
                        # Intelligence check: If the expert result doesn't mention a medicinal plant, 
                        # flag it as a non-medicinal or unknown input.
                        # Since parsed_result is a dict now:
                        identification = expert_result.get("identification_details", {})
                        if isinstance(identification, dict):
                            botanical_details = str(identification).lower()
                        else:
                            botanical_details = str(identification).lower()
                            
                        if "not a leaf" in botanical_details or "not a plant" in botanical_details or "confidence: 0" in botanical_details:
                             response["predicted_plant"] = "Non-Medicinal / Not a Plant"
                             response["expert_notes"] = "AI Expert rejected this image as it does not contain a medicinal leaf."
                        else:
                             response["expert_notes"] = "This sample was verified and clarified by the AI expert."
                    else:
                        response["expert_verification_status"] = "empty_result"
                else:
                    response["expert_verification_status"] = "not_initialized"
        except Exception as gem_err:
            logger.error(f"Graceful fallback: Gemini Expert Verification failed: {gem_err}")
            response["expert_verification_status"] = f"error: {str(gem_err)[:50]}"
            response["expert_notes"] = "Expert verification currently unavailable, using local model identification."
        
        # Add plant details if found
        if plant:
            response["plant_details"] = {
                "id": plant.id,
                "species_name": plant.species_name,
                "common_name": plant.common_name_en,
                "description": plant.description,
                "image_url": plant.image_url
            }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch")
async def predict_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Batch prediction for multiple images
    
    - **files**: List of image files
    - Returns: List of predictions
    """
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 10 images allowed per batch"
            )
        
        results = []
        ml_service = get_ml_service()
        
        for file in files:
            try:
                # Validate file type
                if not file.content_type.startswith('image/'):
                    results.append({
                        "filename": file.filename,
                        "error": "File must be an image"
                    })
                    continue
                
                # Read and predict
                image_bytes = await file.read()
                prediction_result = ml_service.predict(image_bytes)
                
                # Ensure Grad-CAM is generated if H5 model is available
                gradcam_base64 = None
                if ml_service.h5_model: # Assuming ml_service has an attribute h5_model
                    try:
                        # You'll need to pass the correct input format (e.g., preprocessed image)
                        # and the predicted index to get_gradcam_base64.
                        # This example assumes ml_service.predict returns enough info or
                        # that ml_service can provide the h5_input and pred_idx.
                        # For a batch, this might require re-processing the image for h5_input.
                        # For simplicity, let's assume ml_service.predict can return h5_input and pred_idx
                        # or that get_gradcam_base64 can work with image_bytes directly.
                        # If not, further changes to ml_service.predict or image preprocessing would be needed.
                        
                        # Placeholder for h5_input and pred_idx.
                        # In a real scenario, these would come from the prediction process.
                        # For now, we'll use dummy values or assume ml_service.predict provides them.
                        # If ml_service.predict already returns gradcam_base64, this block is redundant.
                        
                        # Assuming prediction_result contains 'h5_input' and 'predicted_class_index'
                        h5_input = prediction_result.get("h5_input") # This might need to be generated here
                        pred_idx = prediction_result.get("predicted_class_index")
                        
                        if h5_input is not None and pred_idx is not None:
                            gradcam_base64 = get_gradcam_base64(ml_service.h5_model, h5_input, int(pred_idx))
                        else:
                            logger.warning("Could not generate Grad-CAM: Missing h5_input or predicted_class_index from prediction_result.")
                    except Exception as gce:
                        logger.warning(f"Grad-CAM generation failed for {file.filename}: {gce}")

                results.append({
                    "filename": file.filename,
                    "predicted_plant": prediction_result["predicted_class"],
                    "confidence": prediction_result["confidence"],
                    "gradcam_base64": gradcam_base64, # Add gradcam to batch result
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "total": len(files),
            "successful": sum(1 for r in results if r.get("success", False)),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.get("/history")
async def get_prediction_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get user's prediction history
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        predictions = db.query(Prediction).order_by(
            Prediction.created_at.desc()
        ).offset(skip).limit(limit).all()
        
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
        
        return {
            "total": db.query(Prediction).count(),
            "skip": skip,
            "limit": limit,
            "predictions": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.post("/{prediction_id}/feedback")
async def submit_feedback(
    prediction_id: int,
    correct: bool,
    comment: str = None,
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a prediction
    
    - **prediction_id**: ID of the prediction
    - **correct**: Whether the prediction was correct
    - **comment**: Optional feedback comment
    """
    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        prediction.feedback_correct = correct
        prediction.feedback_comment = comment
        db.commit()
        
        return {
            "message": "Feedback submitted successfully",
            "prediction_id": prediction_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

