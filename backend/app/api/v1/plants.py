from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.plant import Plant
from typing import List, Optional

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
def list_plants(search: str = "", page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    """
    Query the finalized high-fidelity botanical database.
    Supports clinical search by name or family.
    """
    query = db.query(Plant)
    
    if search:
        query = query.filter(
            (Plant.species_name.ilike(f"%{search}%")) |
            (Plant.common_name_en.ilike(f"%{search}%")) |
            (Plant.family.ilike(f"%{search}%"))
        )
    
    total = query.count()
    plants = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "success": True,
        "plants": [
            {
                "id": p.model_key,
                "common_name": p.common_name_en,
                "scientific_name": p.species_name,
                "family": p.family,
                "description": p.description,
                "iucn_status": p.iucn_status,
                "ayurvedic_balance": p.ayurvedic_balance
            } for p in plants
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{model_key}")
def get_plant(model_key: str, db: Session = Depends(get_db)):
    """
    Fetch a detailed botanical monograph by Model Key.
    """
    plant = db.query(Plant).filter(Plant.model_key == model_key).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Botanical Monograph not found.")
    
    return {
        "success": True,
        "plant": {
            "model_key": plant.model_key,
            "species_name": plant.species_name,
            "common_name": plant.common_name_en,
            "regional_names": {
                "hi": plant.common_name_hi,
                "ta": plant.common_name_ta,
                "te": plant.common_name_te,
                "bn": plant.common_name_bn
            },
            "family": plant.family,
            "description": plant.description,
            "mechanism_of_action": plant.mechanism_of_action,
            "synergy_partners": plant.synergy_partners,
            "ayurvedic_balance": plant.ayurvedic_balance,
            "iucn_status": plant.iucn_status,
            "image_url": plant.image_url,
            "properties": [
                {
                    "ailment": prop.ailment,
                    "usage": prop.usage_description,
                    "compounds": prop.active_compounds
                } for prop in plant.medicinal_properties
            ]
        }
    }
