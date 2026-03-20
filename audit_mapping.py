from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import json

# DB Setup
DATABASE_URL = "sqlite:///./backend/medicinal_plants.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def audit_db():
    db = SessionLocal()
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT id, species_name, common_name_en FROM plants LIMIT 10")).fetchall()
        print("📊 Plants Table (Top 10):")
        for row in result:
            print(f"ID: {row[0]}, Species: {row[1]}, Common: {row[2]}")
        
        # Check Total Count
        count = db.execute(text("SELECT COUNT(*) FROM plants")).scalar()
        print(f"\n📈 Total Plants in DB: {count}")
        
        # Load Model Classes
        class_names_path = r"d:\PROJECT STAGE 1\backend\ml_models\class_names.json"
        if os.path.exists(class_names_path):
            with open(class_names_path, 'r') as f:
                classes = json.load(f)
            print(f"🧠 Total Classes in Model: {len(classes)}")
            
            # Check for Mismatches
            print("\n🔍 Checking for mismatches (Classes in Model but NOT in DB)...")
            mismatches = []
            for name in classes:
                exists = db.execute(text("SELECT 1 FROM plants WHERE species_name = :n"), {"n": name}).scalar()
                if not exists:
                    mismatches.append(name)
            
            if mismatches:
                print(f"⚠️ Found {len(mismatches)} mismatches:")
                print(mismatches[:5], "...")
            else:
                print("✅ All model classes exist in DB!")
        else:
            print("❌ class_names.json not found!")
            
    finally:
        db.close()

if __name__ == "__main__":
    audit_db()
