import sys
import os
import logging
import json
from sqlalchemy.orm import Session

# Add the parent directory to the python path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine, Base
from app.models.plant import Plant, MedicinalProperty

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_best_match(model_key, knowledge_base):
    """Fuzzy match model keys to knowledge base keys"""
    # Direct match
    if model_key in knowledge_base:
        return knowledge_base[model_key]
    
    # Normalized match
    norm_key = model_key.replace('_', ' ').strip().lower()
    for kb_key, data in knowledge_base.items():
        if kb_key.lower() == norm_key:
            return data
        if any(name.lower() == norm_key for name in data.get("common_names", [])):
            return data
            
    return None

def seed_data():
    """Industrial Grade Seeder - Synchronizes Neural Forge Classes with Botanical DB"""
    logger.info("Initializing G9 Monolith Seeding Protocol...")
    db = SessionLocal()
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Paths relative to backend root
        backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        class_names_path = os.path.join(backend_root, "app", "data", "class_names.json")
        kb_path = os.path.join(backend_root, "app", "data", "medicinal_knowledge.json")
        
        if not os.path.exists(class_names_path) or not os.path.exists(kb_path):
            logger.error(f"Required files missing: {class_names_path} or {kb_path}")
            return

        with open(class_names_path, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb = json.load(f)
            
        logger.info(f"Loaded {len(class_names)} taxa from Neural Registry and {len(kb)} entries from KB.")

        count = 0
        for entry in class_names:
            # Extract the actual name string from the dictionary
            model_key = entry.get("name", "Unknown") if isinstance(entry, dict) else str(entry)
            
            # Check if exists
            existing = db.query(Plant).filter(Plant.model_key == model_key).first()
            if existing:
                continue

            data = get_best_match(model_key, kb)
            
            # Default values if no KB match found
            species_name = data.get("scientific_name", model_key.replace('_', ' ').title()) if data else model_key.replace('_', ' ').title()
            common_name = data.get("common_names", [model_key.replace('_', ' ').title()])[0] if data else model_key.replace('_', ' ').title()
            
            plant = Plant(
                model_key=model_key,
                species_name=species_name,
                common_name_en=common_name,
                family=data.get("family", "N/A") if data else "N/A",
                description=data.get("description", f"Medicinal species identified as {common_name} within the G9 Clinical Registry.") if data else f"Medicinal plant identification: {common_name}",
                mechanism_of_action=data.get("description", "Mechanism of action under clinical review.") if data else "Pharmacological profile pending.",
                synergy_partners=data.get("synergy_partners", ["Tulsi", "Ginger"]) if data else ["Tulsi", "Ginger"],
                ayurvedic_balance=data.get("ayurvedic_balance", {"vata": "neutral", "pitta": "neutral", "kapha": "neutral"}) if data else {"vata": "neutral", "pitta": "neutral", "kapha": "neutral"},
                iucn_status=data.get("iucn_status", "Least Concern") if data else "Safe",
                image_url=data.get("image_url", "") if data else ""
            )
            
            db.add(plant)
            db.flush() # Get ID for properties
            
            # Seed properties
            properties_to_add = []
            if data and "ayurvedic_uses" in data:
                for use in data["ayurvedic_uses"]:
                    properties_to_add.append(MedicinalProperty(
                        plant_id=plant.id,
                        ailment=use,
                        usage_description=data.get("preparation", "Consult a qualified Ayurvedic practitioner for preparation guidance."),
                        preparation_method=data.get("preparation", ""),
                        dosage="As directed by physician",
                        source="Ayurvedic Monograph"
                    ))
            else:
                # Basic default property
                properties_to_add.append(MedicinalProperty(
                    plant_id=plant.id,
                    ailment="General Wellness",
                    usage_description=f"Traditionally used in regional medicine for systemic health.",
                    source="G9 Registry"
                ))
                
            for prop in properties_to_add:
                db.add(prop)
                
            count += 1
            if count % 10 == 0:
                logger.info(f"Processed {count} species...")

        db.commit()
        logger.info(f"--- SEEDING COMPLETE: {count} NEW SPECIES SYNCHRONIZED ---")

    except Exception as e:
        logger.error(f"Seeding Failure: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
