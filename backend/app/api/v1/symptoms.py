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
        # Use the hardened gemini_service recommendation logic
        result = await get_symptom_recommendations(symptoms)
        if "error" in result:
            return result
            
        # Ensure we only recommend plants from our available list (simple filtering for demonstration)
        filtered_recs = []
        for rec in result.get("recommendations", []):
            # If the recommended plant isn't in our 3D model list, we still show it but mark it as 'External Reference'
            # For this MVP, we just return the Gemini expertise
            filtered_recs.append(rec)
            
        return {"recommendations": filtered_recs, "lifestyle_advice": result.get("lifestyle_advice"), "diet_tip": result.get("diet_tip")}
        
    except Exception as e:
        logger.error(f"Symptom Search Error: {e}\n{traceback.format_exc()}")
        return {"error": f"Service temporarily unavailable: {str(e)[:100]}"}
