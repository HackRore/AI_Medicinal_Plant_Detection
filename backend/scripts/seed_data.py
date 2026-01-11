"""
Database Seed Script
Populate database with Indian medicinal plant information
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.plant import Plant, MedicinalProperty
from app.models.user import User
from app.models.prediction import Prediction, Favorite

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_plants(db):
    """Seed plant data"""
    print("\nSeeding plant data...")
    
    plants_data = [
        {
            "species_name": "Azadirachta_indica",
            "common_name_en": "Neem",
            "common_name_hi": "नीम",
            "common_name_ta": "வேம்பு",
            "common_name_te": "వేప",
            "common_name_bn": "নিম",
            "scientific_classification": {
                "kingdom": "Plantae",
                "family": "Meliaceae",
                "genus": "Azadirachta"
            },
            "description": "Neem is a tree in the mahogany family Meliaceae. It is one of two species in the genus Azadirachta, and is native to the Indian subcontinent. It is typically grown in tropical and semi-tropical regions. Neem trees have been used in traditional medicine for thousands of years.",
            "medicinal_properties": [
                {
                    "ailment": "Skin infections",
                    "usage_description": "Neem has antibacterial and antifungal properties that help treat various skin infections",
                    "preparation_method": "Grind neem leaves into a paste and apply topically",
                    "dosage": "Apply 2-3 times daily",
                    "precautions": "May cause skin irritation in sensitive individuals. Avoid during pregnancy.",
                    "efficacy_rating": 5,
                    "source": "Traditional Ayurvedic medicine"
                },
                {
                    "ailment": "Diabetes",
                    "usage_description": "Neem leaves help regulate blood sugar levels",
                    "preparation_method": "Consume fresh neem leaves or make a decoction",
                    "dosage": "4-5 leaves daily on empty stomach",
                    "precautions": "Monitor blood sugar levels. Consult doctor if on diabetes medication.",
                    "efficacy_rating": 4,
                    "source": "Clinical studies"
                }
            ]
        },
        {
            "species_name": "Ocimum_sanctum",
            "common_name_en": "Holy Basil (Tulsi)",
            "common_name_hi": "तुलसी",
            "common_name_ta": "துளசி",
            "common_name_te": "తులసి",
            "common_name_bn": "তুলসী",
            "scientific_classification": {
                "kingdom": "Plantae",
                "family": "Lamiaceae",
                "genus": "Ocimum"
            },
            "description": "Holy Basil, also known as Tulsi, is an aromatic perennial plant in the family Lamiaceae. It is native to the Indian subcontinent and widespread as a cultivated plant throughout the Southeast Asian tropics. Tulsi is cultivated for religious and traditional medicine purposes.",
            "medicinal_properties": [
                {
                    "ailment": "Respiratory infections",
                    "usage_description": "Tulsi has antimicrobial properties that help fight respiratory infections",
                    "preparation_method": "Make a tea by boiling leaves in water",
                    "dosage": "2-3 cups of tulsi tea daily",
                    "precautions": "Generally safe. May interact with blood thinning medications.",
                    "efficacy_rating": 5,
                    "source": "Traditional Ayurvedic medicine"
                },
                {
                    "ailment": "Stress and anxiety",
                    "usage_description": "Tulsi is an adaptogen that helps reduce stress and anxiety",
                    "preparation_method": "Consume fresh leaves or make tea",
                    "dosage": "5-6 leaves daily or 2 cups of tea",
                    "precautions": "Safe for most people. Avoid excessive consumption during pregnancy.",
                    "efficacy_rating": 4,
                    "source": "Clinical research"
                }
            ]
        },
        {
            "species_name": "Aloe_barbadensis",
            "common_name_en": "Aloe Vera",
            "common_name_hi": "घृतकुमारी",
            "common_name_ta": "கற்றாழை",
            "common_name_te": "కలబంద",
            "common_name_bn": "ঘৃতকুমারী",
            "scientific_classification": {
                "kingdom": "Plantae",
                "family": "Asphodelaceae",
                "genus": "Aloe"
            },
            "description": "Aloe vera is a succulent plant species of the genus Aloe. The plant is stemless or very short-stemmed with thick, greenish, fleshy leaves. It is widely cultivated for its medicinal and agricultural uses.",
            "medicinal_properties": [
                {
                    "ailment": "Burns and wounds",
                    "usage_description": "Aloe vera gel has cooling and healing properties for burns and wounds",
                    "preparation_method": "Extract gel from fresh leaves and apply directly",
                    "dosage": "Apply 2-3 times daily",
                    "precautions": "Test for allergic reactions. Do not apply to deep wounds.",
                    "efficacy_rating": 5,
                    "source": "Clinical studies"
                },
                {
                    "ailment": "Digestive issues",
                    "usage_description": "Aloe vera juice helps with digestion and constipation",
                    "preparation_method": "Extract juice from leaves or use commercial preparation",
                    "dosage": "30-60ml juice daily",
                    "precautions": "May cause diarrhea. Avoid during pregnancy and breastfeeding.",
                    "efficacy_rating": 4,
                    "source": "Traditional medicine"
                }
            ]
        },
        {
            "species_name": "Curcuma_longa",
            "common_name_en": "Turmeric",
            "common_name_hi": "हल्दी",
            "common_name_ta": "மஞ்சள்",
            "common_name_te": "పసుపు",
            "common_name_bn": "হলুদ",
            "scientific_classification": {
                "kingdom": "Plantae",
                "family": "Zingiberaceae",
                "genus": "Curcuma"
            },
            "description": "Turmeric is a flowering plant of the ginger family, Zingiberaceae. It is a perennial, rhizomatous, herbaceous plant native to the Indian subcontinent and Southeast Asia. The rhizomes are used in cooking and traditional medicine.",
            "medicinal_properties": [
                {
                    "ailment": "Inflammation",
                    "usage_description": "Curcumin in turmeric has powerful anti-inflammatory effects",
                    "preparation_method": "Mix turmeric powder with warm milk or water",
                    "dosage": "1-3 grams daily",
                    "precautions": "May interact with blood thinners. High doses may cause digestive issues.",
                    "efficacy_rating": 5,
                    "source": "Clinical research"
                },
                {
                    "ailment": "Joint pain",
                    "usage_description": "Helps reduce joint pain and arthritis symptoms",
                    "preparation_method": "Consume as supplement or in food",
                    "dosage": "500mg-2g daily",
                    "precautions": "Consult doctor if on medication. May cause stomach upset.",
                    "efficacy_rating": 4,
                    "source": "Clinical trials"
                }
            ]
        },
        {
            "species_name": "Withania_somnifera",
            "common_name_en": "Ashwagandha",
            "common_name_hi": "अश्वगंधा",
            "common_name_ta": "அமுக்கரா",
            "common_name_te": "అశ్వగంధ",
            "common_name_bn": "অশ্বগন্ধা",
            "scientific_classification": {
                "kingdom": "Plantae",
                "family": "Solanaceae",
                "genus": "Withania"
            },
            "description": "Ashwagandha is a plant in the Solanaceae or nightshade family. Several other species in the genus Withania are morphologically similar. It is commonly used in Ayurvedic medicine as an adaptogen.",
            "medicinal_properties": [
                {
                    "ailment": "Stress and fatigue",
                    "usage_description": "Ashwagandha is an adaptogen that helps combat stress and fatigue",
                    "preparation_method": "Consume as powder mixed with milk or water",
                    "dosage": "300-500mg twice daily",
                    "precautions": "Avoid during pregnancy. May interact with thyroid medications.",
                    "efficacy_rating": 5,
                    "source": "Clinical studies"
                },
                {
                    "ailment": "Immunity",
                    "usage_description": "Boosts immune system function",
                    "preparation_method": "Take as supplement or powder",
                    "dosage": "250-600mg daily",
                    "precautions": "May cause drowsiness. Avoid with immunosuppressants.",
                    "efficacy_rating": 4,
                    "source": "Traditional Ayurvedic medicine"
                }
            ]
        },
        {
            "species_name": "Mentha_arvensis",
            "common_name_en": "Mint",
            "common_name_hi": "पुदीना",
            "common_name_ta": "புதினா",
            "common_name_te": "పుదీనా",
            "common_name_bn": "পুদিনা",
            "scientific_classification": {
                "kingdom": "Plantae",
                "family": "Lamiaceae",
                "genus": "Mentha"
            },
            "description": "Mint is a genus of plants in the family Lamiaceae. It is estimated that 13 to 24 species exist. The species are widely distributed across Europe, Africa, Asia, Australia, and North America.",
            "medicinal_properties": [
                {
                    "ailment": "Digestive problems",
                    "usage_description": "Mint helps relieve indigestion, gas, and bloating",
                    "preparation_method": "Make tea from fresh or dried leaves",
                    "dosage": "2-3 cups of mint tea daily",
                    "precautions": "Generally safe. May worsen acid reflux in some people.",
                    "efficacy_rating": 4,
                    "source": "Traditional medicine"
                },
                {
                    "ailment": "Headache",
                    "usage_description": "Mint oil can help relieve tension headaches",
                    "preparation_method": "Apply diluted mint oil to temples",
                    "dosage": "As needed",
                    "precautions": "Dilute essential oil before topical use. Avoid contact with eyes.",
                    "efficacy_rating": 3,
                    "source": "Clinical observations"
                }
            ]
        }
    ]
    
    for plant_data in plants_data:
        # Check if plant already exists
        existing_plant = db.query(Plant).filter(
            Plant.species_name == plant_data["species_name"]
        ).first()
        
        if existing_plant:
            print(f"  - {plant_data['species_name']} already exists, skipping...")
            continue
        
        # Extract medicinal properties
        medicinal_props = plant_data.pop("medicinal_properties")
        
        # Create plant
        plant = Plant(**plant_data)
        db.add(plant)
        db.flush()  # Get the plant ID
        
        # Add medicinal properties
        for prop_data in medicinal_props:
            prop = MedicinalProperty(
                plant_id=plant.id,
                **prop_data
            )
            db.add(prop)
        
        print(f"  ✓ Added {plant_data['species_name']}")
    
    db.commit()
    print(f"\n✓ Seeded {len(plants_data)} plants successfully")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("DATABASE SEEDING SCRIPT")
    print("AI Medicinal Plant Detection System")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed plants
        seed_plants(db)
        
        print("\n" + "=" * 60)
        print("✓ DATABASE SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
