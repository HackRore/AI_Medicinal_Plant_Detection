"""
Plants API Routes
CRUD operations for plant information
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.plant import Plant, MedicinalProperty

router = APIRouter()


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

