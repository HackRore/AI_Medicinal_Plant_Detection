import sqlite3
import json
import os

db_path = 'c:/Users/Dell/Downloads/HackRore/AI_Medicinal_Plant_Detection/backend/medicinal_plants.db'
class_names_path = 'c:/Users/Dell/Downloads/HackRore/AI_Medicinal_Plant_Detection/backend/ml_models/class_names.json'

def audit():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT count(*) FROM plants")
    total_plants = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM plants WHERE image_url IS NOT NULL AND image_url != ''")
    plants_with_images = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM plants WHERE description NOT LIKE 'Medicinal plant:%' AND description != 'Coming soon.' AND description != ''")
    plants_with_custom_desc = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM medicinal_properties")
    total_properties = cursor.fetchone()[0]
    
    print(f"Total plants in DB: {total_plants}")
    print(f"Plants with images: {plants_with_images}")
    print(f"Plants with custom descriptions: {plants_with_custom_desc}")
    print(f"Total medicinal property entries: {total_properties}")
    
    cursor.execute("SELECT species_name, image_url, description FROM plants WHERE species_name IN ('Tulsi', 'Neem', 'Aloevera')")
    samples = cursor.fetchall()
    print("\nSample Plant Data:")
    for row in samples:
        print(f"Species: {row[0]}")
        print(f"Image: {row[1]}")
        print(f"Desc: {row[2][:50]}...")
    
    conn.close()

if __name__ == '__main__':
    audit()
