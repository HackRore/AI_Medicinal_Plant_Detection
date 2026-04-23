"""
Prediction Model
Database model for storing user predictions and feedback
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Prediction(Base):
    """Prediction model for storing ML predictions"""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    image_url = Column(String, nullable=False)
    predicted_plant_id = Column(Integer, ForeignKey("plants.id"))
    confidence_score = Column(Float)
    model_version = Column(String)
    ensemble_used = Column(Boolean, default=False)
    feedback_correct = Column(Boolean, nullable=True)
    feedback_comment = Column(String, nullable=True)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, confidence={self.confidence_score})>"


class Favorite(Base):
    """User favorites for plants"""
    
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, plant_id={self.plant_id})>"
