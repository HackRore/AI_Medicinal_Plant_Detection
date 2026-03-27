from fastapi import APIRouter
import os, re, json, logging, traceback
from app.config import settings
from app.services.gemini_service import get_gemini_service

logger = logging.getLogger(__name__)
router = APIRouter()

AVAILABLE_PLANTS = [
    "Aloevera", "Amla", "Amruthaballi", "Ashwagandha", "Bamboo",
    "Betel", "Bhrami", "Bringaraja", "Catharanthus", "Chilly",
    "Coffee", "Curry_Leaf", "Drumstick", "Ginger", "Giloy",
    "Guava", "Hibiscus", "Lemon", "Moringa", "Neem",
    "Peppermint", "Tulsi", "Turmeric"
]

def safe_parse(text: str) -> dict:
    if not text:
        return {"error": "Empty response from AI"}
    try:
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', text).strip()
        return json.loads(cleaned)
    except Exception:
        pass
    try:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"error": "Could not parse AI response", "raw": text[:100]}

@router.post("/symptom-search")
async def symptom_search(payload: dict):
    symptoms = payload.get("symptoms", "").strip()
    if not symptoms:
        return {"error": "Please describe your symptoms"}
        
    try:
        gemini = get_gemini_service()
        if not gemini.initialized:
            return {"error": "Ayurvedic AI search is currently offline. Please configure GEMINI_API_KEY."}

        prompt = f"""You are a senior Ayurvedic physician with 30 years of clinical experience.
A patient describes their symptoms: "{symptoms}"

Task: From this list of locally available medicinal plants ONLY: {", ".join(AVAILABLE_PLANTS)}
Recommend exactly 3 plants that best address these symptoms according to Ayurvedic principles.

Return ONLY a valid JSON object with the following structure:
{{
  "recommendations": [
    {{
      "plant": "Plant Name",
      "scientific_name": "Scientific Name",
      "ayurvedic_name": "Sanskrit/Ayurvedic Name",
      "why": "Specific reason for recommendation based on symptoms",
      "preparation": "How to prepare the remedy (e.g., decoction, paste)",
      "dosage": "Suggested frequency and timing",
      "dosha_effect": "How it balances Vata, Pitta, or Kapha",
      "active_compounds": "Key phytochemicals",
      "safety": "Contraindications or precautions",
      "classical_reference": "Ayurvedic text reference (e.g., Charaka Samhita)"
    }}
  ],
  "lifestyle_advice": "One specific Ayurvedic lifestyle recommendation",
  "diet_tip": "One seasonal/Ayurvedic dietary tip",
  "warning": "Standard medical disclaimer"
}}
CRITICAL: Return ONLY raw JSON. No markdown backticks. No extra text."""

        response_text = await gemini.generate_text(prompt, model_id="gemini-2.0-flash")
        result = safe_parse(response_text)
        return result
        
    except Exception as e:
        logger.error(f"Symptom Search Error: {e}")
        return {"error": f"Service temporarily unavailable: {str(e)[:100]}"}
