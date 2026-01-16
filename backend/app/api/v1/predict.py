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

from app.database import get_db
from app.services.ml_service import get_ml_service
from app.models.prediction import Prediction
from app.models.plant import Plant
from app.config import settings

router = APIRouter()


@router.post("/")
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
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file size
        if len(image_bytes) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Get ML service and make prediction
        ml_service = get_ml_service()
        start_time = time.time()
        prediction_result = ml_service.predict(image_bytes)
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Find plant in database - Superior Rejection Logic
        CONFIDENCE_THRESHOLD = 0.65
        GAP_THRESHOLD = 0.15
        
        predicted_class = prediction_result["predicted_class"]
        confidence = prediction_result["confidence"]
        top_predictions = prediction_result.get("top_predictions", [])
        
        # Calculate gap between top 1 and top 2
        gap = 1.0  # Default if only one class exists
        if len(top_predictions) >= 2:
            gap = top_predictions[0]["confidence"] - top_predictions[1]["confidence"]
        
        is_robust = confidence >= CONFIDENCE_THRESHOLD and gap >= GAP_THRESHOLD
        
        if not is_robust:
             # Low confidence or ambiguous - likely not a medicinal leaf or confused
             plant = None
             if not is_robust:
                 if confidence < CONFIDENCE_THRESHOLD:
                     predicted_class = "Unknown / Not a Medicinal Leaf"
                 else:
                     predicted_class = "Ambiguous Input / Multiple Species Detected"
        else:
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
        
        # Prepare response
        response = {
            "prediction_id": prediction_record.id,
            "predicted_plant": predicted_class,
            "confidence": prediction_result["confidence"],
            "top_predictions": prediction_result["top_predictions"],
            "processing_time_ms": processing_time,
            "model_version": prediction_result["model_version"],
            "plant_details": None
        }
        
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
                
                results.append({
                    "filename": file.filename,
                    "predicted_plant": prediction_result["predicted_class"],
                    "confidence": prediction_result["confidence"],
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

