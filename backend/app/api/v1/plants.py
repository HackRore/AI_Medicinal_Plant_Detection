"""
Plants API Routes
CRUD operations for plant information
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
import os
import json
from app.models.plant import Plant, MedicinalProperty
from app.database import get_db
from app.core.fallback_data import PLANT_FALLBACK

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


# Fallback logic is now imported from app.core.fallback_data

@router.get("/")
def get_plants(search: str = "", db: Session = Depends(get_db)):
    # Try database first
    try:
        plants = db.query(Plant).all()
        if plants and len(plants) > 0:
            db_list = []
            for p in plants:
                item = {c.name: getattr(p, c.name) for c in p.__table__.columns}
                # Harmonize for frontend: ensure common_name and species_name
                item["common_name"] = item.get("common_name_en") or item.get("species_name")
                db_list.append(item)
                
            if search:
                db_list = [p for p in db_list if search.lower() in p.get("common_name","").lower()]
            return {"plants": db_list, "total": len(db_list), "source": "database"}
    except Exception:
        pass

    # Fallback logic
    result = PLANT_FALLBACK
    if search:
        result = [p for p in result if search.lower() in p.get("common_name", "").lower()
                  or search.lower() in p.get("description", "").lower()]
    return {"plants": result, "total": len(result), "source": "fallback"}


@router.get("/{plant_id}")
async def get_plant(plant_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific plant
    """
    try:
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        
        if plant:
            # Get medicinal properties from DB
            properties = db.query(MedicinalProperty).filter(
                MedicinalProperty.plant_id == plant_id
            ).all()
            
            return {
                "id": plant.id,
                "species_name": plant.species_name,
                "common_names": {
                    "en": plant.common_name_en or plant.species_name,
                    "hi": plant.common_name_hi or "",
                    "ta": plant.common_name_ta or "",
                    "te": plant.common_name_te or "",
                    "bn": plant.common_name_bn or ""
                },
                "scientific_classification": plant.scientific_classification or "Not specified",
                "description": plant.description or "No description available",
                "image_url": plant.image_url or "https://via.placeholder.com/800x600?text=No+Image",
                "medicinal_properties": [
                    {
                        "ailment": prop.ailment,
                        "usage": prop.usage_description,
                        "preparation": prop.preparation_method,
                        "dosage": prop.dosage,
                        "precautions": prop.precautions
                    }
                    for prop in properties
                ],
                "source": "database"
            }
    except Exception:
        # If DB query fails or plant not found in DB, try fallback
        pass

    # Fallback logic
    fallback_plant = next((p for p in PLANT_FALLBACK if p["id"] == plant_id), None)
    if not fallback_plant:
        if 1 <= plant_id <= len(PLANT_FALLBACK):
            fallback_plant = PLANT_FALLBACK[plant_id - 1]
        else:
            raise HTTPException(status_code=404, detail="Plant not found")

    # Map fallback to frontend structure
    return {
        "id": fallback_plant.get("id"),
        "species_name": fallback_plant.get("species_name", "Unknown"),
        "common_names": fallback_plant.get("common_names", {"en": fallback_plant.get("common_name", "Unknown")}),
        "scientific_classification": fallback_plant.get("scientific_classification", "Botany"),
        "description": fallback_plant.get("description", "No description available in fallback."),
        "image_url": fallback_plant.get("image_url", "https://via.placeholder.com/800x600?text=No+Image"),
        "medicinal_properties": fallback_plant.get("medicinal_properties", [
            {
                "ailment": "General Wellness",
                "usage": "Standard use",
                "preparation": "Decoction",
                "dosage": "As needed",
                "precautions": "Consult professional"
            }
        ]),
        "source": "fallback"
    }
     
    # The original except blocks are now redundant because the first try-except handles DB errors
    # and the fallback logic handles not found cases.
    # If an HTTPException is raised within the fallback logic, it will propagate.
    # If any other unexpected error occurs in the fallback logic, it will also propagate.
    # The structure of the provided instruction implies these should be removed or adjusted.
    # Given the instruction, I'll remove the redundant outer try-except.
    # The `except HTTPException` and `except Exception as e` were part of the original structure
    # but the new code structure handles the exceptions differently.
    # The instruction shows them *after* the new fallback logic, which is syntactically incorrect.
    # I will assume the intent is to replace the original try-except block with the new logic.
    # The `except HTTPException` and `except Exception as e` at the end of the instruction are misplaced.
    # I will remove them as the new structure handles errors more granularly.
    # The `try` block now only covers the DB access. If it fails, it falls through to the fallback.
    # If the fallback fails to find a plant, it raises HTTPException.
    # So, the outer try-except is no longer needed.
    # I will remove the outer try-except and keep the inner one for DB access.
    # The instruction has `except HTTPException: raise` and `except Exception as e: raise HTTPException`
    # *after* the fallback return, which is syntactically impossible.
    # I will interpret this as the user wanting to remove the outer try-except and let the
    # HTTPException from the fallback propagate, and any other error in the fallback also propagate.
    # The `try...except Exception` block around the DB query is sufficient.
    # The `raise HTTPException(status_code=404, detail="Plant not found")` is now handled by the fallback.
    # The `raise HTTPException(status_code=500, detail=f"Failed to get plant: {str(e)}")` is also handled by the `except Exception` block.
    # So, the final `except` blocks in the instruction are indeed redundant and should be removed.


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

