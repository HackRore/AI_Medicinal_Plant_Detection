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

        core_plants = {
            "Neem": {
                "species": "Neem",
                "hi": "नीम",
                "desc": "Powerful antimicrobial and skin-healing tree native to India.",
                "props": [("Skin diseases", "Leaf paste application", "2-3 times daily", "Safe externally; avoid high oral doses")]
            },
            "Tulsi": {
                "species": "Tulsi",
                "hi": "तুলसी",
                "desc": "Sacred adaptogen used for respiratory health and stress relief.",
                "props": [("Cold & Cough", "Boil leaves in water (Tea)", "2 cups daily", "Avoid during pregnancy")]
            },
            "Aloevera": {
                "species": "Aloevera",
                "hi": "घृतकुमारी",
                "desc": "Succulent with thick gel used for burns, skin care, and digestion.",
                "props": [("Burns/Skin", "Direct gel application", "As needed", "Avoid yellow latex layer")]
            },
            "Turmeric": {
                "species": "Turmeric",
                "hi": "हल्दी",
                "desc": "Bright orange rhizome with potent anti-inflammatory curcumin.",
                "props": [("Inflammation", "Mix with milk or honey", "1 tsp daily", "High doses may interfere with blood thinners")]
            },
            "Ashwagandha": {
                "species": "Ashwagandha",
                "hi": "अश्वगंधा",
                "desc": "Renowned adaptogen used for strength, vitality, and immunity.",
                "props": [("Stress/Anxiety", "Root powder with milk", "1-2 tsp daily", "Consult doctor if hyperthyroid")]
            },
            "Mint": {
                "species": "Mint",
                "hi": "पुदीना",
                "desc": "Cooling herb used for digestion, oral health, and headaches.",
                "props": [("Digestion", "Fresh leaves or juice", "As needed", "Generally safe")]
            },
            "Amla": {
                "species": "Amla",
                "hi": "आंवला",
                "desc": "Richest source of Vitamin C; improves immunity and hair health.",
                "props": [("Immunity", "Raw fruit or juice", "10-20ml daily", "Safe for most")]
            },
            "Amruthaballi": {
                "species": "Amruthaballi",
                "hi": "गिलोय",
                "desc": "Versatile herb (Giloy) used for chronic fevers and immunity.",
                "props": [("Chronic Fever", "Boiled stem extract", "30ml daily", "Safe; monitors blood sugar if diabetic")]
            },
            "Ginger": {
                "species": "Ginger",
                "hi": "अदरक",
                "desc": "Warming rhizome used for nausea and digestive warmth.",
                "props": [("Nausea", "Fresh juice with honey", "1-2 tsp", "Avoid in excessive heat")]
            },
            "Betel": {
                "species": "Betel",
                "hi": "पान",
                "desc": "Heart-shaped leaf used as digestive stimulant and antiseptic.",
                "props": [("Digestion", "Chew fresh leaves", "After meals", "Avoid with tobacco")]
            },
            "Doddpathre": {
                 "species": "Doddpathre",
                 "hi": "अजवाइन पत्र",
                 "desc": "Indian Borage; excellent for infant cough and digestion.",
                 "props": [("Infant Cough", "Warm juice with honey", "5ml", "Very safe for children")]
            },
            "Drumstick": {
                 "species": "Drumstick",
                 "hi": "सहजन",
                 "desc": "Moringa; superfood with high mineral content.",
                 "props": [("Nutritional boost", "Cooked leaves or pods", "Regular diet", "None")]
            }
        }

        seeded_count = 0
        for cls_name in classes:
            # Check if exists
            existing = db.query(Plant).filter(Plant.species_name == cls_name).first()
            if existing:
                continue

            # Find matching core data by species name or common name
            core_info = {}
            for k, v in core_plants.items():
                if v["species"] == cls_name or k == cls_name:
                    core_info = v
                    break
            
            plant = Plant(
                model_key=cls_name.lower().replace('_', '-'),
                species_name=cls_name,
                common_name_en=core_info.get("common_name", cls_name.replace('_', ' ').title()),
                common_name_hi=core_info.get("hi", ""),
                description=core_info.get("desc", f"Medicinal species: {cls_name.replace('_', ' ')}. Detailed botanical profile coming soon.")
            )
            db.add(plant)
            db.flush() # Get plant ID

            # Add properties if available
            if "props" in core_info:
                for ailment, usage, dose, caution in core_info["props"]:
                    prop = MedicinalProperty(
                        plant_id=plant.id,
                        ailment=ailment,
                        usage_description=usage,
                        dosage=dose,
                        precautions=caution,
                        source="Traditional Ayurvedic Knowledge"
                    )
                    db.add(prop)
            
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

