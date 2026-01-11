"""
Plant Model
Database model for medicinal plant information
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Plant(Base):
    """Plant model for medicinal plant information"""
    
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    species_name = Column(String, unique=True, index=True, nullable=False)
    common_name_en = Column(String)
    common_name_hi = Column(String)
    common_name_ta = Column(String)
    common_name_te = Column(String)
    common_name_bn = Column(String)
    scientific_classification = Column(JSON)  # Store taxonomy as JSON
    description = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    medicinal_properties = relationship("MedicinalProperty", back_populates="plant")
    
    def __repr__(self):
        return f"<Plant(id={self.id}, species={self.species_name})>"


class MedicinalProperty(Base):
    """Medicinal properties and uses of plants"""
    
    __tablename__ = "medicinal_properties"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    ailment = Column(String, index=True)
    usage_description = Column(Text)
    preparation_method = Column(Text)
    dosage = Column(Text)
    precautions = Column(Text)
    efficacy_rating = Column(Integer)  # 1-5 scale
    source = Column(String)  # Reference source
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    plant = relationship("Plant", back_populates="medicinal_properties")
    
    def __repr__(self):
        return f"<MedicinalProperty(id={self.id}, ailment={self.ailment})>"
