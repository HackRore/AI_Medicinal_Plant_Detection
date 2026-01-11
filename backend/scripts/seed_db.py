
import sys
import os
import logging
from sqlalchemy.orm import Session

# Add the parent directory to the python path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine, Base
from app.models.plant import Plant, MedicinalProperty

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    """Seed the database with initial medicinal plants"""
    db = SessionLocal()
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Check if data already exists
        if db.query(Plant).count() > 0:
            logger.info("Database already contains data. Skipping seed.")
            return

        logger.info("Seeding database with medicinal plants...")

        plants_data = [
            {
                "species_name": "Ocimum_tenuiflorum",
                "common_name_en": "Holy Basil (Tulsi)",
                "common_name_hi": "तुलसी (Tulsi)",
                "common_name_ta": "துளசி (Thulasi)",
                "common_name_te": "తులసి (Tulasi)",
                "common_name_bn": "তুলসী (Tulsi)",
                "scientific_classification": "Kingdom: Plantae, Family: Lamiaceae, Genus: Ocimum",
                "description": "Tulsi is considered a sacred plant in Hinduism and is revered as an avatar of Lakshmi. It is an aromatic perennial plant in the family Lamiaceae. It is native to the Indian subcontinent and widespread as a cultivated plant throughout the Southeast Asian tropics.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Ocimum_tenuiflorum_macro_2.jpg",
                "properties": [
                    {
                        "ailment": "Common Cold & Cough",
                        "usage_description": "Leaves are boiled with tea or ginger to clear respiratory passages.",
                        "preparation_method": "Boil 5-6 fresh leaves with water, ginger, and honey. Drink warm.",
                        "dosage": "Twice a day",
                        "precautions": "Avoid excessive consumption during pregnancy.",
                        "efficacy_rating": 5,
                        "source": "Ayurveda"
                    },
                    {
                        "ailment": "Stress & Anxiety",
                        "usage_description": "Acts as an adaptogen to help body adapt to stress.",
                        "preparation_method": "Chew 2-3 clean leaves daily morning.",
                        "dosage": "Once daily",
                        "precautions": "None",
                        "efficacy_rating": 4,
                        "source": "Traditional Knowledge"
                    }
                ]
            },
            {
                "species_name": "Azadirachta_indica",
                "common_name_en": "Neem",
                "common_name_hi": "नीम (Neem)",
                "common_name_ta": "வேம்பு (Vembu)",
                "common_name_te": "వేప (Vepa)",
                "common_name_bn": "নিম (Nim)",
                "scientific_classification": "Kingdom: Plantae, Family: Meliaceae, Genus: Azadirachta",
                "description": "Neem is a tree in the mahogany family Meliaceae. It is one of two species in the genus Azadirachta, and is native to the Indian subcontinent. It is typically grown in tropical and semi-tropical regions.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Neem_leaves.jpg/1200px-Neem_leaves.jpg",
                "properties": [
                    {
                        "ailment": "Skin Infections",
                        "usage_description": "Antifungal and antibacterial properties help treat acne and rashes.",
                        "preparation_method": "Make a paste of fresh leaves and apply to affected area.",
                        "dosage": "Apply once daily for 20 mins",
                        "precautions": "Might cause irritation on sensitive skin.",
                        "efficacy_rating": 5,
                        "source": "Ayurveda"
                    }
                ]
            },
            {
                "species_name": "Aloe_vera",
                "common_name_en": "Aloe Vera",
                "common_name_hi": "घृतकुमारी (Ghritkumari)",
                "common_name_ta": "கற்றாழை (Kathalai)",
                "common_name_te": "కలబంద (Kalabanda)",
                "common_name_bn": "ঘৃতকুমারী (Ghritkumari)",
                "scientific_classification": "Kingdom: Plantae, Family: Asphod乐acceae, Genus: Aloe",
                "description": "Aloe vera is a succulent plant species of the genus Aloe. It is widely distributed, and is considered an invasive species in many world regions. An evergreen perennial, it originates from the Arabian Peninsula.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Aloe_vera_flower_insets.png",
                "properties": [
                    {
                        "ailment": "Burns & Sunburn",
                        "usage_description": "Soothing gel cools and heals burnt skin.",
                        "preparation_method": "Extract fresh gel from leaf and apply directly.",
                        "dosage": "As needed",
                        "precautions": "External use only unless processed.",
                        "efficacy_rating": 5,
                        "source": "Modern Medicine"
                    }
                ]
            },
            {
                "species_name": "Mentha",
                "common_name_en": "Mint",
                "common_name_hi": "पुदीना (Pudina)",
                "common_name_ta": "புதினா (Pudina)",
                "common_name_te": "పుదీనా (Pudina)",
                "common_name_bn": "পুদিনা (Pudina)",
                "scientific_classification": "Kingdom: Plantae, Family: Lamiaceae, Genus: Mentha",
                "description": "Mint is a genus of plants in the family Lamiaceae (mint family). The species are not clearly distinct and estimates of the number of species vary from 13 to 18.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Mint-leaves-2009.jpg/1200px-Mint-leaves-2009.jpg",
                "properties": [
                    {
                        "ailment": "Indigestion",
                        "usage_description": "Helps soothe stomach upsets and indigestion.",
                        "preparation_method": "Chew fresh leaves or make mint tea.",
                        "dosage": "After meals",
                        "precautions": "Avoid if you have GERD.",
                        "efficacy_rating": 4,
                        "source": "Traditional Knowledge"
                    }
                ]
            },
            {
                "species_name": "Tinospora_cordifolia",
                "common_name_en": "Giloy",
                "common_name_hi": "गिलोय (Giloy)",
                "common_name_ta": "சீந்தில் (Seenthil)",
                "common_name_te": "తిప్ప తీగ (Tippa Teega)",
                "common_name_bn": "গুলঞ্চ (Gulancha)",
                "scientific_classification": "Kingdom: Plantae, Family: Menispermaceae, Genus: Tinospora",
                "description": "Tinospora cordifolia, which is known by the common names heart-leaved moonseed, guduchi, and giloy, is a herbaceous vine of the family Menispermaceae indigenous to tropical regions of the Indian subcontinent.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Tinospora_cordifolia_leaves.jpg",
                "properties": [
                    {
                        "ailment": "Immunity Booster",
                        "usage_description": "Modulates the immune system (immunomodulator).",
                        "preparation_method": "Boil stem in water to make decoction.",
                        "dosage": "50ml once daily",
                        "precautions": "Consult doctor if diabetic.",
                        "efficacy_rating": 5,
                        "source": "Ayurveda"
                    }
                ]
            }
        ]

        for p_data in plants_data:
            properties = p_data.pop("properties")
            plant = Plant(**p_data)
            db.add(plant)
            db.flush() # Get ID

            for prop_data in properties:
                prop = MedicinalProperty(**prop_data, plant_id=plant.id)
                db.add(prop)
        
        db.commit()
        logger.info("Successfully seeded database with 5 plants.")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
