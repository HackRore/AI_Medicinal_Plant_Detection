from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.database import SessionLocal
import os, json, base64, time, logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

FEEDBACK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             "..", "..", "..", "ml_models", "feedback_queue")

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

@router.get("/feedback-stats")
async def get_feedback_stats():
    """Returns statistics on accumulated hard negatives for the retraining queue."""
    try:
        os.makedirs(FEEDBACK_DIR, exist_ok=True)
        meta_path = os.path.join(FEEDBACK_DIR, "mismatch_log.jsonl")
        
        if not os.path.exists(meta_path):
            return {"total_reports": 0, "queue_ready": False, "message": "No feedback collected yet."}
        
        entries = []
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except:
                    pass
        
        # Group by predicted class to identify confusion pairs
        confusion_pairs = {}
        for e in entries:
            key = f"{e.get('predicted_class')} → {e.get('correct_class')}"
            confusion_pairs[key] = confusion_pairs.get(key, 0) + 1
        
        top_confusions = sorted(confusion_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_reports": len(entries),
            "queue_ready": len(entries) >= 50,  # Trigger retrain at 50+ reports
            "top_confusion_pairs": [{"pair": k, "count": v} for k, v in top_confusions],
            "message": f"Retraining queue: {len(entries)} samples collected." + 
                       (" Ready for next retrain cycle!" if len(entries) >= 50 else f" {50 - len(entries)} more needed to trigger retrain.")
        }
    except Exception as e:
        return {"error": str(e), "total_reports": 0}
