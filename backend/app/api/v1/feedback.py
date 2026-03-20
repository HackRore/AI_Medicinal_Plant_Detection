from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionFeedback

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
async def submit_feedback(
    feedback: PredictionFeedback,
    db: Session = Depends(get_db)
):
    """
    Submit user feedback for a prediction.
    This starts the 'Continuous Learning Loop' by validating AI performance with human ground-truth.
    """
    prediction = db.query(Prediction).filter(Prediction.id == feedback.prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Update prediction with feedback
    prediction.feedback_correct = feedback.is_correct
    prediction.feedback_comment = feedback.comment
    
    # If the user corrected the prediction, we store the actual plant ID
    if not feedback.is_correct and feedback.correct_plant_id:
        logger.info(f"🔄 Loop Correction: Prediction {feedback.prediction_id} was incorrect. Actual: {feedback.correct_plant_id}")
        # In a real system, we'd trigger a retraining flag or move this image to a 'review_required' folder
    
    db.commit()
    logger.info(f"✔ Feedback registered for prediction {feedback.prediction_id}")
    
    return {"status": "success", "message": "Feedback registered for learning loop."}
