"""
Plants API Routes
CRUD operations for plant information
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.plant import Plant, MedicinalProperty

import os
import json
from app.models.plant import Plant, MedicinalProperty
from app.database import get_db

router = APIRouter()


@router.post("/admin/seed")
async def seed_database(db: Session = Depends(get_db)):
    """
    Temporary administrative endpoint to seed the production database.
    Populates 6 core medicinal plants with details and placeholders for others.
    """
    try:
        # 1. Load class names from model
        class_names_path = os.path.join("ml_models", "class_names.json")
        if not os.path.exists(class_names_path):
            raise HTTPException(status_code=404, detail="class_names.json not found")
            
        with open(class_names_path, 'r') as f:
            classes = json.load(f)

        # 2. Define core data for the top 6 species
        core_plants = {
            "Azadirachta_indica": {
                "common_name": "Neem",
                "common_name_hi": "नीम",
                "description": "Powerful antimicrobial and skin-healing tree native to India."
            },
            "Ocimum_sanctum": {
                "common_name": "Holy Basil (Tulsi)",
                "common_name_hi": "तुलसी",
                "description": "Sacred adaptogen used for respiratory health and stress relief."
            },
            "Aloe_barbadensis": {
                "common_name": "Aloe Vera",
                "common_name_hi": "घृतकुमारी",
                "description": "Succulent with thick gel used for burns, skin care, and digestion."
            },
            "Curcuma_longa": {
                "common_name": "Turmeric",
                "common_name_hi": "हल्दी",
                "description": "Bright orange rhizome with potent anti-inflammatory curcumin."
            },
            "Withania_somnifera": {
                "common_name": "Ashwagandha",
                "common_name_hi": "अश्वगंधा",
                "description": "Renowned adaptogen used for strength, vitality, and immunity."
            },
            "Mentha_arvensis": {
                "common_name": "Mint",
                "common_name_hi": "पुदीना",
                "description": "Cooling herb used for digestion, oral health, and headaches."
            }
        }

        seeded_count = 0
        for cls_name in classes:
            # Check if exists
            existing = db.query(Plant).filter(Plant.species_name == cls_name).first()
            if existing:
                continue

            core_info = core_plants.get(cls_name, {})
            
            plant = Plant(
                model_key=cls_name.lower().replace('_', '-'),
                species_name=cls_name,
                common_name_en=core_info.get("common_name", cls_name.replace('_', ' ').title()),
                common_name_hi=core_info.get("common_name_hi", ""),
                description=core_info.get("description", f"Medicinal species: {cls_name.replace('_', ' ')}. Detailed botanical profile coming soon.")
            )
            db.add(plant)
            seeded_count += 1
            
        db.commit()
        return {"status": "success", "seeded_count": seeded_count, "total_classes": len(classes)}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")


@router.get("/")
async def list_plants(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all medicinal plants with pagination
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **search**: Optional search query
    """
    try:
        query = db.query(Plant)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Plant.species_name.ilike(search_filter)) |
                (Plant.common_name_en.ilike(search_filter)) |
                (Plant.description.ilike(search_filter))
            )
        
        total = query.count()
        plants = query.offset(skip).limit(limit).all()
        
        results = []
        for plant in plants:
            results.append({
                "id": plant.id,
                "species_name": plant.species_name,
                "common_name": plant.common_name_en,
                "common_name_hi": plant.common_name_hi,
                "description": plant.description[:200] + "..." if plant.description and len(plant.description) > 200 else plant.description,
                "image_url": plant.image_url
            })
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "plants": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list plants: {str(e)}")


@router.get("/{plant_id}")
async def get_plant(plant_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific plant
    
    - **plant_id**: Plant ID
    """
    try:
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        # Get medicinal properties
        properties = db.query(MedicinalProperty).filter(
            MedicinalProperty.plant_id == plant_id
        ).all()
        
        return {
            "id": plant.id,
            "species_name": plant.species_name,
            "common_names": {
                "en": plant.common_name_en,
                "hi": plant.common_name_hi,
                "ta": plant.common_name_ta,
                "te": plant.common_name_te,
                "bn": plant.common_name_bn
            },
            "scientific_classification": plant.scientific_classification,
            "description": plant.description,
            "image_url": plant.image_url,
            "medicinal_properties": [
                {
                    "ailment": prop.ailment,
                    "usage": prop.usage_description,
                    "preparation": prop.preparation_method,
                    "dosage": prop.dosage,
                    "precautions": prop.precautions,
                    "efficacy_rating": prop.efficacy_rating,
                    "source": prop.source
                }
                for prop in properties
            ],
            "created_at": plant.created_at.isoformat() if plant.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plant: {str(e)}")


@router.get("/{plant_id}/medicinal")
async def get_medicinal_properties(plant_id: int, db: Session = Depends(get_db)):
    """
    Get medicinal properties of a plant
    
    - **plant_id**: Plant ID
    """
    try:
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        properties = db.query(MedicinalProperty).filter(
            MedicinalProperty.plant_id == plant_id
        ).all()
        
        return {
            "plant_id": plant_id,
            "plant_name": plant.species_name,
            "properties": [
                {
                    "id": prop.id,
                    "ailment": prop.ailment,
                    "usage_description": prop.usage_description,
                    "preparation_method": prop.preparation_method,
                    "dosage": prop.dosage,
                    "precautions": prop.precautions,
                    "efficacy_rating": prop.efficacy_rating,
                    "source": prop.source
                }
                for prop in properties
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get medicinal properties: {str(e)}")


@router.get("/search/by-name")
async def search_plants(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """
    Search plants by name (scientific or common)
    
    - **q**: Search query
    """
    try:
        search_filter = f"%{q}%"
        plants = db.query(Plant).filter(
            (Plant.species_name.ilike(search_filter)) |
            (Plant.common_name_en.ilike(search_filter)) |
            (Plant.common_name_hi.ilike(search_filter))
        ).limit(20).all()
        
        results = []
        for plant in plants:
            results.append({
                "id": plant.id,
                "species_name": plant.species_name,
                "common_name": plant.common_name_en,
                "image_url": plant.image_url
            })
        
        return {
            "query": q,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

