from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from app.database import SessionLocal
import os, json, base64, time, logging
from datetime import datetime

from app.services.feedback_service import feedback_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/report-mismatch")
async def report_mismatch(
    file: UploadFile = File(...),
    predicted_class: str = Form(...),
    correct_class: str = Form("unknown"),
    user_note: str = Form("")
):
    """
    Sprint 5: Active Learning Feedback Loop
    Every 'Report Mismatch' click from the frontend sends the hard negative
    to the retraining queue for the next monthly retrain cycle.
    """
    try:
        os.makedirs(FEEDBACK_DIR, exist_ok=True)
        
        raw = await file.read()
        timestamp = int(time.time())
        
        # Save image to feedback queue
        img_filename = f"mismatch_{timestamp}_{predicted_class[:20]}.jpg"
        img_path = os.path.join(FEEDBACK_DIR, img_filename)
        with open(img_path, "wb") as f:
            f.write(raw)
        
        # Log metadata
        meta_path = os.path.join(FEEDBACK_DIR, "mismatch_log.jsonl")
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "image_file": img_filename,
            "predicted_class": predicted_class,
            "correct_class": correct_class,
            "user_note": user_note,
            "file_size_kb": round(len(raw) / 1024, 1)
        }
        with open(meta_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        
        logger.info(f"Feedback received: {predicted_class} -> {correct_class}")
        
        return {
            "success": True,
            "message": "Thank you! This image has been added to our retraining queue. Our model will improve from your feedback.",
            "feedback_id": f"fb_{timestamp}",
            "queued_for_retrain": True
        }
    except Exception as e:
        logger.error(f"Feedback logging error: {e}")
        raise HTTPException(500, f"Failed to log feedback: {str(e)}")

@router.post("/correction")
async def log_correction(payload: dict):
    """Log a user correction for a prediction."""
    pred_id = payload.get("prediction_id")
    correct_species = payload.get("correct_species")
    
    if not pred_id or not correct_species:
        raise HTTPException(400, "prediction_id and correct_species are required")
    
    success = feedback_service.log_correction(pred_id, correct_species)
    if success:
        return {"success": True, "message": "Thank you! Your correction helps improve PlantoAI."}
    else:
        raise HTTPException(500, "Failed to log correction")

@router.get("/stats")
async def get_stats(request: Request):
    """Get correction stats (Admin only)."""
    admin_key = request.headers.get("X-Admin-Key")
    if admin_key != os.environ.get("SECRET_KEY"):
        raise HTTPException(403, "Unauthorized access")
    
    stats = feedback_service.get_correction_stats()
    return {"success": True, "stats": stats}

