from sqlalchemy import Column, String, JSON, DateTime, Integer
from sqlalchemy.sql import func
# from app.database import Base

class GeminiCache(Base):
    """Cache for Gemini AI Vision results to save costs and latency"""
    __tablename__ = "gemini_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    image_hash = Column(String, unique=True, index=True, nullable=False)
    response_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
