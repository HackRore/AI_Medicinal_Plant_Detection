import json
import os
import sys

# Ensure we are in backend dir
if not os.path.exists("app"):
    print("Please run from backend directory.")
    sys.exit(1)

from sqlalchemy.orm import sessionmaker
from app.database import Base, engine, SessionLocal
from app.models.plant import Plant

print("Initializing DB...")
Base.metadata.create_all(bind=engine)
db = SessionLocal()

with open('ml_models/class_names.json') as f:
    classes = json.load(f)

seeded = 0
for cls in classes:
    exists = db.query(Plant).filter(Plant.species_name == cls).first()
    if not exists:
        p = Plant(
            species_name=cls,
            common_name_en=cls.replace('_', ' '),
            description=f"Medicinal information for {cls.replace('_', ' ')}."
        )
        db.add(p)
        seeded += 1
db.commit()
print(f"Successfully seeded {seeded} new plants into the database. Total classes: {len(classes)}.")
