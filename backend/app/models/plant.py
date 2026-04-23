from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Plant(Base):
    """
    PREMIUM BOTANICAL ENGINE MODEL
    Stores high-fidelity medicinal plant intelligence.
    """
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    model_key = Column(String, unique=True, index=True, nullable=False)
    species_name = Column(String, index=True, nullable=False) # Not unique because typos in class labels (Gauva/Guava)
    
    # Regional Nomenclature
    common_name_en = Column(String, index=True)
    common_name_hi = Column(String)
    common_name_ta = Column(String)
    common_name_te = Column(String)
    common_name_bn = Column(String)
    
    # Intelligence Data
    family = Column(String, index=True)
    scientific_classification = Column(JSON) 
    description = Column(Text)
    
    # Premium Insights
    mechanism_of_action = Column(Text) # Clinical biology
    synergy_partners = Column(JSON)    # Compatible herbs
    ayurvedic_balance = Column(JSON)   # Vata/Pitta/Kapha mapping
    iucn_status = Column(String)       # Conservation status
    
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    medicinal_properties = relationship("MedicinalProperty", back_populates="plant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Plant(id={self.id}, species={self.species_name})>"

class MedicinalProperty(Base):
    """
    CLINICAL MEDICINAL SCHEMA
    Detailed ailment/remedy mapping with efficacy ratings.
    """
    __tablename__ = "medicinal_properties"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    
    ailment = Column(String, index=True)
    usage_description = Column(Text)
    preparation_method = Column(Text)
    dosage = Column(Text)
    precautions = Column(Text)
    active_compounds = Column(JSON)
    
    efficacy_rating = Column(Integer, default=5) # Neural verification score
    source = Column(String) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    plant = relationship("Plant", back_populates="medicinal_properties")
    
    def __repr__(self):
        return f"<MedicinalProperty(id={self.id}, ailment={self.ailment})>"
