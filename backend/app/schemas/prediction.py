from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PredictionFeedback(BaseModel):
    prediction_id: int = Field(..., description="ID of the prediction to provide feedback for")
    is_correct: bool = Field(..., description="Whether the prediction was correct")
    correct_plant_id: Optional[int] = Field(None, description="If incorrect, the actual ID of the plant")
    comment: Optional[str] = Field(None, description="Optional user comment")

class PredictionBase(BaseModel):
    predicted_plant_id: Optional[int] = None
    confidence_score: float
    model_version: str
    ensemble_used: bool = False
    processing_time_ms: float

class PredictionResponse(PredictionBase):
    id: int
    image_url: str
    created_at: datetime
    feedback_correct: Optional[bool] = None
    
    class Config:
        from_attributes = True
