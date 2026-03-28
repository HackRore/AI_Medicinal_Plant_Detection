from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
import os
import json

from app.database import get_db
from app.models.plant import Plant, MedicinalProperty

router = APIRouter()

# ── Step 6: Hardcoded Fallback ────────────────────────────────────
PLANT_FALLBACK = [
    {"id":1,"name":"Aloevera","scientific_name":"Aloe barbadensis miller","family":"Asphodelaceae","ayurvedic_name":"Kumari","medicinal_uses":"Burns, wound healing, digestive disorders, anti-inflammatory, skin conditions","parts_used":"Leaf gel, latex","preparation":"Gel applied topically; juice 20ml twice daily","active_compounds":"Aloin, acemannan, anthraquinones","toxicity":"Gel safe externally; latex avoid prolonged use","description":"Succulent plant with powerful healing gel"},
    {"id":2,"name":"Neem","scientific_name":"Azadirachta indica","family":"Meliaceae","ayurvedic_name":"Nimba","medicinal_uses":"Antibacterial, antifungal, blood purifier, skin diseases, dental hygiene","parts_used":"Leaves, bark, seeds, oil","preparation":"Leaf paste, decoction, oil, twig as toothbrush","active_compounds":"Nimbin, nimbidin, azadirachtin, quercetin","toxicity":"Safe medicinally; seed oil toxic in high doses","description":"The village pharmacy of India"},
    {"id":3,"name":"Tulsi","scientific_name":"Ocimum tenuiflorum","family":"Lamiaceae","ayurvedic_name":"Tulasi","medicinal_uses":"Respiratory disorders, stress, fever, antibacterial, adaptogen, immunity","parts_used":"Leaves, seeds, roots, oil","preparation":"10 fresh leaves chewed daily; decoction as tea","active_compounds":"Eugenol, rosmarinic acid, ursolic acid, linalool","toxicity":"Safe; avoid large doses in pregnancy","description":"Queen of Ayurvedic herbs"},
    {"id":4,"name":"Turmeric","scientific_name":"Curcuma longa","family":"Zingiberaceae","ayurvedic_name":"Haridra","medicinal_uses":"Anti-inflammatory, antioxidant, wound healing, liver support, joint pain","parts_used":"Rhizome","preparation":"Powder in food, golden milk, paste","active_compounds":"Curcumin, bisdemethoxycurcumin, turmerone","toxicity":"Safe in food doses; avoid with blood thinners","description":"Most scientifically studied natural compound"},
    {"id":5,"name":"Ashwagandha","scientific_name":"Withania somnifera","family":"Solanaceae","ayurvedic_name":"Ashwagandha","medicinal_uses":"Adaptogen, anxiety, stamina, anti-inflammatory, thyroid support","parts_used":"Root, leaves, berries","preparation":"Root powder in warm milk; 3-6g daily","active_compounds":"Withanolides, withaferin A, sitoindosides","toxicity":"Avoid in pregnancy and autoimmune conditions","description":"3000-year-old Ayurvedic rejuvenator"},
    {"id":6,"name":"Giloy","scientific_name":"Tinospora cordifolia","family":"Menispermaceae","ayurvedic_name":"Guduchi","medicinal_uses":"Immune booster, fever, diabetes, antioxidant, liver protection, arthritis","parts_used":"Stem, roots, leaves","preparation":"Stem decoction, powder, juice, kadha","active_compounds":"Tinosporine, berberine, tinosporic acid","toxicity":"Safe; monitor blood sugar if diabetic","description":"Called Amrita — nectar of immortality"},
    {"id":7,"name":"Amla","scientific_name":"Phyllanthus emblica","family":"Phyllanthaceae","ayurvedic_name":"Amalaki","medicinal_uses":"Vitamin C, hair growth, immunity, digestion, anti-aging, liver protection","parts_used":"Fruit, leaves, bark, seeds","preparation":"Raw fruit, juice, churna powder, hair oil","active_compounds":"Emblicanin A and B, ascorbic acid, gallic acid","toxicity":"Non-toxic; safe for all ages","description":"Contains as much Vitamin C as 20 oranges"},
    {"id":8,"name":"Brahmi","scientific_name":"Bacopa monnieri","family":"Plantaginaceae","ayurvedic_name":"Brahmi","medicinal_uses":"Memory, cognitive function, anxiety, ADHD, neuroprotection","parts_used":"Whole plant","preparation":"Fresh juice, powder, ghee infusion","active_compounds":"Bacosides A and B, brahmine, herpestine","toxicity":"Safe; nausea on empty stomach; avoid in hypothyroidism","description":"NASA studied for cognitive stress reduction"},
    {"id":9,"name":"Ginger","scientific_name":"Zingiber officinale","family":"Zingiberaceae","ayurvedic_name":"Shunthi","medicinal_uses":"Nausea, digestion, anti-inflammatory, cold and flu, pain relief","parts_used":"Rhizome","preparation":"Fresh juice, decoction, powder, tea","active_compounds":"Gingerols, shogaols, paradols, zingerone","toxicity":"Safe in food amounts; high doses cause heartburn","description":"Used for 5000 years across every medicine system"},
    {"id":10,"name":"Moringa","scientific_name":"Moringa oleifera","family":"Moringaceae","ayurvedic_name":"Shigru","medicinal_uses":"Malnutrition, anti-inflammatory, blood sugar, antioxidant, lactation","parts_used":"Leaves, seeds, pods, roots","preparation":"Leaf powder, fresh leaves cooked, seed oil","active_compounds":"Isothiocyanates, quercetin, chlorogenic acid","toxicity":"Leaves and pods safe; root bark toxic","description":"7x Vitamin C of oranges, 4x calcium of milk"},
    {"id":11,"name":"Neem","scientific_name":"Azadirachta indica","family":"Meliaceae","ayurvedic_name":"Nimba","medicinal_uses":"Skin diseases, blood purifier, antifungal, antibacterial, dental care","parts_used":"Leaves, bark, seeds, oil","preparation":"Leaf paste, decoction, twig as toothbrush","active_compounds":"Nimbin, azadirachtin, limonoids","toxicity":"Safe; avoid seed oil in large doses","description":"Sarva roga nivarini — curer of all ailments"},
    {"id":12,"name":"Hibiscus","scientific_name":"Hibiscus rosa-sinensis","family":"Malvaceae","ayurvedic_name":"Japa","medicinal_uses":"Blood pressure, hair growth, liver protection, cholesterol","parts_used":"Flowers, leaves, roots","preparation":"Flower tea, hair oil, paste","active_compounds":"Anthocyanins, hibiscin, quercetin, vitamin C","toxicity":"Generally safe; avoid high doses in pregnancy","description":"Lowers blood pressure as effectively as some medications"},
    {"id":13,"name":"Lemongrass","scientific_name":"Cymbopogon citratus","family":"Poaceae","ayurvedic_name":"Bhustrina","medicinal_uses":"Anxiety, fever, pain relief, antifungal, antibacterial, cholesterol","parts_used":"Stems, leaves, essential oil","preparation":"Tea, essential oil diffusion, decoction","active_compounds":"Citral, geraniol, limonene, myrcene","toxicity":"Safe as tea; essential oil toxic if ingested","description":"Most potent natural antifungal agent"},
    {"id":14,"name":"Peppermint","scientific_name":"Mentha piperita","family":"Lamiaceae","ayurvedic_name":"Pudina","medicinal_uses":"IBS, headaches, nausea, decongestant, digestion, antispasmodic","parts_used":"Leaves, essential oil","preparation":"Tea, essential oil, fresh leaves, capsules","active_compounds":"Menthol, m蛋白質","toxicity":"Safe as tea; never use essential oil on infants","description":"Natural hybrid — crossed between watermint and spearmint"},
    {"id":15,"name":"Fenugreek","scientific_name":"Trigonella foenum-graecum","family":"Fabaceae","ayurvedic_name":"Methi","medicinal_uses":"Diabetes, cholesterol, digestion, lactation, testosterone","parts_used":"Seeds, leaves","preparation":"Soaked seeds, powder, decoction, fresh leaves in food","active_compounds":"Diosgenin, trigonelline, galactomannan, saponins","toxicity":"Safe in food; high doses cause diarrhea; avoid in pregnancy","description":"Compounds structurally similar to insulin"},
]

@router.get("/")
def get_plants(search: str = "", db: Session = Depends(get_db)):
    """Get all plants — tries Supabase first, falls back to local data."""
    try:
        from sqlalchemy import text
        if search:
            result = db.execute(
                text("SELECT * FROM plants WHERE LOWER(name) LIKE :s OR LOWER(medicinal_uses) LIKE :s ORDER BY name"),
                {"s": f"%{search.lower()}%"}
            )
        else:
            result = db.execute(text("SELECT * FROM plants ORDER BY name"))
        rows = result.mappings().all()
        plants = [dict(row) for row in rows]
        if plants:
            return {"plants": plants, "total": len(plants), "source": "supabase"}
    except Exception as e:
        print(f"DB error, using fallback: {e}")

    # Fallback — always works
    result = PLANT_FALLBACK
    if search:
        result = [p for p in result if
                  search.lower() in p["name"].lower() or
                  search.lower() in p.get("medicinal_uses", "").lower()]
    return {"plants": result, "total": len(result), "source": "fallback"}

# ── Administrative Endpoints ──────────────────────────────────────
@router.post("/admin/migrate")
def migrate_database(db: Session = Depends(get_db)):
    """Remote migration endpoint to seed plants into Supabase."""
    try:
        from app.db.migrate import CREATE_TABLE, PLANTS_DATA
        db.execute(text(CREATE_TABLE))
        db.commit()
        
        for p in PLANTS_DATA:
            db.execute(text("""
                INSERT INTO plants (name, scientific_name, family, ayurvedic_name,
                    medicinal_uses, parts_used, preparation, active_compounds,
                    toxicity, description, habitat)
                VALUES (:name, :sci, :fam, :ayu, :med, :parts, :prep, :comp, :tox, :desc, :hab)
                ON CONFLICT (name) DO UPDATE SET
                    scientific_name = EXCLUDED.scientific_name,
                    medicinal_uses = EXCLUDED.medicinal_uses,
                    updated_at = NOW()
            """), {
                "name": p[0], "sci": p[1], "fam": p[2], "ayu": p[3],
                "med": p[4], "parts": p[5], "prep": p[6], "comp": p[7],
                "tox": p[8], "desc": p[9], "hab": p[10]
            })
        db.commit()
        return {"status": "success", "message": f"Seeded {len(PLANTS_DATA)} plants"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@router.get("/{plant_id}")
async def get_plant_detail(plant_id: int, db: Session = Depends(get_db)):
    """Get detail for a specific plant (DB with fallback)"""
    try:
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        if plant: return plant
    except: pass
    
    for p in PLANT_FALLBACK:
        if p["id"] == plant_id: return p
    raise HTTPException(status_code=404, detail="Plant not found")
