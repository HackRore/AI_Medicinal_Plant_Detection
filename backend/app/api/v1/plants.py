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


# Hardcoded fallback — survives ALL Render restarts, zero DB dependency
PLANT_FALLBACK = [
    {"id":1,"name":"Aloevera","scientific_name":"Aloe barbadensis miller","family":"Asphodelaceae","medicinal_uses":"Burns, wound healing, digestive disorders, anti-inflammatory, skin conditions","ayurvedic_name":"Kumari","parts_used":"Leaf gel, latex","preparation":"Gel applied topically; juice 20ml twice daily","toxicity":"Gel safe externally; latex avoid prolonged use","description":"Succulent plant with powerful healing gel used worldwide in medicine and cosmetics","active_compounds":"Aloin, acemannan, anthraquinones, vitamins A, C, E"},
    {"id":2,"name":"Neem","scientific_name":"Azadirachta indica","family":"Meliaceae","medicinal_uses":"Antibacterial, antifungal, blood purifier, skin diseases, dental hygiene, malaria","ayurvedic_name":"Nimba","parts_used":"Leaves, bark, seeds, oil","preparation":"Leaf paste, decoction, oil, twig as toothbrush","toxicity":"Safe medicinally; seed oil toxic in high doses; avoid in pregnancy","description":"The village pharmacy of India — every part has documented medicinal value","active_compounds":"Nimbin, nimbidin, azadirachtin, quercetin, limonoids"},
    {"id":3,"name":"Tulsi","scientific_name":"Ocimum tenuiflorum","family":"Lamiaceae","medicinal_uses":"Respiratory disorders, stress, fever, antibacterial, adaptogen, immunity","ayurvedic_name":"Tulasi","parts_used":"Leaves, seeds, roots, oil","preparation":"10 fresh leaves chewed daily; decoction as tea","toxicity":"Safe; avoid large doses in pregnancy; may slow clotting","description":"Queen of herbs in Ayurveda — sacred, aromatic, and clinically proven adaptogen","active_compounds":"Eugenol, rosmarinic acid, ursolic acid, linalool"},
    {"id":4,"name":"Amla","scientific_name":"Phyllanthus emblica","family":"Phyllanthaceae","medicinal_uses":"Vitamin C, hair growth, immunity, digestion, anti-aging, liver protection","ayurvedic_name":"Amalaki","parts_used":"Fruit, leaves, bark, seeds","preparation":"Raw fruit, juice, churna powder, hair oil","toxicity":"Non-toxic; safe for all ages","description":"Contains as much Vitamin C as 20 oranges — heat stable due to protective tannins","active_compounds":"Emblicanin A and B, ascorbic acid, gallic acid, ellagic acid"},
    {"id":5,"name":"Ashwagandha","scientific_name":"Withania somnifera","family":"Solanaceae","medicinal_uses":"Adaptogen, anxiety, stamina, anti-inflammatory, testosterone, thyroid support","ayurvedic_name":"Ashwagandha","parts_used":"Root, leaves, berries","preparation":"Root powder in warm milk; 3-6g daily","toxicity":"Avoid in pregnancy and autoimmune conditions; interacts with thyroid meds","description":"3000-year-old Ayurvedic rejuvenator — one of the most studied adaptogenic herbs","active_compounds":"Withanolides, withaferin A, sitoindosides, alkaloids"},
    {"id":6,"name":"Giloy","scientific_name":"Tinospora cordifolia","family":"Menispermaceae","medicinal_uses":"Immune booster, fever, diabetes, antioxidant, liver protection, arthritis","ayurvedic_name":"Guduchi","parts_used":"Stem, roots, leaves","preparation":"Stem decoction, powder, juice, kadha","toxicity":"Safe; monitor blood sugar if diabetic; avoid in autoimmune disease","description":"Called Amrita — nectar of immortality — one of only 3 plants with Rasayana status","active_compounds":"Tinosporine, berberine, tinosporic acid, cordifolide"},
    {"id":7,"name":"Turmeric","scientific_name":"Curcuma longa","family":"Zingiberaceae","medicinal_uses":"Anti-inflammatory, antioxidant, wound healing, joint pain, liver, digestion","ayurvedic_name":"Haridra","parts_used":"Rhizome","preparation":"Powder in food, golden milk, paste, capsules","toxicity":"Safe in food doses; high doses cause nausea; avoid with blood thinners","description":"Subject of 12000+ peer-reviewed studies — most scientifically studied natural compound","active_compounds":"Curcumin, bisdemethoxycurcumin, ar-turmerone"},
    {"id":8,"name":"Brahmi","scientific_name":"Bacopa monnieri","family":"Plantaginaceae","medicinal_uses":"Memory, cognitive function, anxiety, ADHD, neuroprotection, epilepsy","ayurvedic_name":"Brahmi","parts_used":"Whole plant","preparation":"Fresh juice, powder, ghee infusion, tablets","toxicity":"Safe; may cause nausea on empty stomach; avoid in hypothyroidism","description":"NASA studied Brahmi for astronauts — proven to reduce cognitive fatigue under stress","active_compounds":"Bacosides A and B, brahmine, herpestine"},
    {"id":9,"name":"Moringa","scientific_name":"Moringa oleifera","family":"Moringaceae","medicinal_uses":"Malnutrition, anti-inflammatory, blood sugar, antioxidant, lactation","ayurvedic_name":"Shigru","parts_used":"Leaves, seeds, pods, roots","preparation":"Leaf powder, fresh leaves cooked, seed oil","toxicity":"Leaves and pods safe; root bark toxic — avoid","description":"Miracle tree: 7x vitamin C of oranges, 4x calcium of milk, 2x protein of yogurt","active_compounds":"Isothiocyanates, quercetin, chlorogenic acid, zeatin"},
    {"id":10,"name":"Ginger","scientific_name":"Zingiber officinale","family":"Zingiberaceae","medicinal_uses":"Nausea, digestion, anti-inflammatory, cold and flu, pain relief, circulation","ayurvedic_name":"Shunthi","parts_used":"Rhizome","preparation":"Fresh juice, decoction, powder, tea","toxicity":"Safe in food amounts; high doses may cause heartburn; caution with blood thinners","description":"Used for 5000 years across every major traditional medicine system in the world","active_compounds":"Gingerols, shogaols, paradols, zingerone"},
    {"id":11,"name":"Hibiscus","scientific_name":"Hibiscus rosa-sinensis","family":"Malvaceae","medicinal_uses":"Blood pressure, hair growth, liver protection, anti-inflammatory, cholesterol","ayurvedic_name":"Japa","parts_used":"Flowers, leaves, roots","preparation":"Flower tea, hair oil, paste","toxicity":"Generally safe; avoid in pregnancy in high doses","description":"Vibrant red flowers used medicinally across Africa, Asia, and Latin America","active_compounds":"Anthocyanins, hibiscin, quercetin, vitamin C"},
    {"id":12,"name":"Fenugreek","scientific_name":"Trigonella foenum-graecum","family":"Fabaceae","medicinal_uses":"Diabetes, cholesterol, digestion, lactation, testosterone, anti-inflammatory","ayurvedic_name":"Methi","parts_used":"Seeds, leaves","preparation":"Soaked seeds, powder, decoction, fresh leaves in food","toxicity":"Safe in food; high doses cause diarrhea; avoid in pregnancy","description":"Seeds contain compounds structurally similar to insulin — proven hypoglycemic effect","active_compounds":"Diosgenin, trigonelline, galactomannan, saponins"},
    {"id":13,"name":"Curry Leaves","scientific_name":"Murraya koenigii","family":"Rutaceae","medicinal_uses":"Diabetes, hair loss, digestion, cholesterol, antioxidant, antibacterial","ayurvedic_name":"Meetha Neem","parts_used":"Leaves, bark, roots","preparation":"Fresh leaves in food, decoction, hair oil","toxicity":"Non-toxic; safe for all ages","description":"Essential in South Indian cuisine — leaves contain alkaloids proven to lower blood sugar","active_compounds":"Mahanimbine, carbazole alkaloids, koenigine, murrayanol"},
    {"id":14,"name":"Lemongrass","scientific_name":"Cymbopogon citratus","family":"Poaceae","medicinal_uses":"Anxiety, fever, pain relief, antifungal, antibacterial, cholesterol, detox","ayurvedic_name":"Bhustrina","parts_used":"Stems, leaves, essential oil","preparation":"Tea, essential oil diffusion, decoction","toxicity":"Safe as tea; essential oil toxic if ingested; avoid in pregnancy","description":"Citral content provides powerful antimicrobial and anti-anxiety effects","active_compounds":"Citral, geraniol, limonene, myrcene, linalool"},
<<<<<<< HEAD
    {"id":15,"name":"Peppermint","scientific_name":"Mentha piperita","family":"Lamiaceae","medicinal_uses":"IBS, headaches, nausea, decongestant, digestion, antispasmodic","ayurvedic_name":"Pudina","parts_used":"Leaves, essential oil","preparation":"Tea, essential oil, fresh leaves, capsules","toxicity":"Safe as tea; essential oil toxic undiluted; never use on infants","description":"A natural hybrid that doesn't exist in the wild — crossed between watermint and spearmint","active_compounds":"Menthol, menthone, menthyl acetate, linalool"},
=======
    {"id":15,"name":"Peppermint","scientific_name":"Mentha piperita","family":"Lamiaceae","medicinal_uses":"IBS, headaches, nausea, decongestant, digestion, antispasmodic","ayurvedic_name":"Pudina","parts_used":"Leaves, essential oil","preparation":"Tea, essential oil, fresh leaves, capsules","toxicity":"Safe as tea; essential oil toxic undiluted; never use on infants","description":"A natural hybrid that doesn't exist in the wild — crossed between watermint and spearmint","active_compounds":"Menthol, menthone, menthyl acetate, limonene"},
>>>>>>> 381b452bb68fcd83567a866ff7e8e5eb92cbb57c
]

@router.get("/")
def get_plants(search: str = "", db: Session = Depends(get_db)):
    # Try database first
    try:
        plants = db.query(Plant).all()
        if plants and len(plants) > 0:
            db_list = [
                {c.name: getattr(p, c.name) for c in p.__table__.columns}
                for p in plants
            ]
            if search:
                db_list = [p for p in db_list if search.lower() in p.get("name","").lower()]
            return {"plants": db_list, "total": len(db_list), "source": "database"}
    except Exception:
        pass

    # Database empty or failed — use fallback (always works)
    result = PLANT_FALLBACK
    if search:
        result = [p for p in result if search.lower() in p["name"].lower()
                  or search.lower() in p.get("medicinal_uses","").lower()]
    return {"plants": result, "total": len(result), "source": "fallback"}


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

