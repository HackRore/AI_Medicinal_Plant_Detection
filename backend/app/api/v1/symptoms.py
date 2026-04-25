from fastapi import APIRouter
import os, re, json, logging, traceback
from app.config import settings
from app.services.gemini_service import get_gemini_service, get_symptom_recommendations

logger = logging.getLogger(__name__)
router = APIRouter()

AVAILABLE_PLANTS = ["Banana", "Mango", "Neem", "Guava", "Jackfruit", "Tulsi", "Aloevera", "Turmeric", "Ashwagandha"]

@router.post("/symptom-search")
async def symptom_search(payload: dict):
    symptoms = payload.get("symptoms", "").strip()
    if not symptoms:
        return {"error": "Please describe your symptoms"}
        
    try:
        # Step 1: Tactical Database Search (High-Confidence Local Matches)
        from app.database import SessionLocal
        from app.models.plant import MedicinalProperty, Plant
        db = SessionLocal()
        
        local_matches = []
        try:
            # Simple keyword search in local clinical monographs
            results = db.query(Plant).join(MedicinalProperty).filter(
                (MedicinalProperty.ailment.ilike(f"%{symptoms}%")) |
                (Plant.description.ilike(f"%{symptoms}%"))
            ).limit(3).all()
            
            for p in results:
                local_matches.append({
                    "plant_name": p.common_name_en,
                    "scientific_name": p.species_name,
                    "reason": "Direct clinical monograph match in Neural Knowledge Base.",
                    "confidence": "VERIFIED",
                    "usage": p.medicinal_properties[0].usage_description if p.medicinal_properties else "See monograph"
                })
        except Exception as db_err:
            logger.warning(f"Local Knowledge Base search bypassed: {db_err}")
        finally:
            db.close()

        # Step 2: Gemini Neural Synthesis (Deep Reasoning)
        result = await get_symptom_recommendations(symptoms)
        if "error" in result and not local_matches:
            return result
            
        combined_recs = local_matches + result.get("recommendations", [])
        
        # Deduplicate and limit
        seen = set()
        final_recs = []
        for r in combined_recs:
            if r['plant_name'].lower() not in seen:
                final_recs.append(r)
                seen.add(r['plant_name'].lower())

        return {
            "recommendations": final_recs[:5], 
            "lifestyle_advice": result.get("lifestyle_advice", "Maintain hydration and rest."), 
            "diet_tip": result.get("diet_tip", "Prefer warm, easily digestible food."),
            "source": "Hybrid Intelligence (G9 Monolith + Gemini)"
        }
        
    except Exception as e:
        logger.error(f"Symptom Search Error: {e}\n{traceback.format_exc()}")
        return {"error": f"Service temporarily unavailable: {str(e)[:100]}"}
