from fastapi import APIRouter
import google.generativeai as genai
import os, re, json
from app.config import settings

router = APIRouter()

AVAILABLE_PLANTS = [
    "Aloevera", "Amla", "Amruthaballi", "Ashwagandha", "Bamboo",
    "Betel", "Bhrami", "Bringaraja", "Catharanthus", "Chilly",
    "Coffee", "Curry_Leaf", "Drumstick", "Ginger", "Giloy",
    "Guava", "Hibiscus", "Lemon", "Moringa", "Neem",
    "Peppermint", "Tulsi", "Turmeric"
]

def safe_parse(text: str) -> dict:
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
    return {"error": "Could not parse response"}

@router.post("/symptom-search")
async def symptom_search(payload: dict):
    symptoms = payload.get("symptoms", "").strip()
    if len(symptoms) < 3:
        return {"error": "Please describe your symptoms in more detail"}
    try:
        # Use settings.GEMINI_API_KEY if available, else fallback to env
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"error": "Gemini API key not configured"}
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""You are a senior Ayurvedic physician with 30 years of clinical experience at an Indian medical institution.

A patient describes: "{symptoms}"

From this list of available medicinal plants only: {", ".join(AVAILABLE_PLANTS)}

Recommend exactly 3 most appropriate plants. Return ONLY raw JSON, no markdown, no backticks:
{{
  "recommendations": [
    {{
      "plant": "Tulsi",
      "scientific_name": "Ocimum tenuiflorum",
      "ayurvedic_name": "Tulasi",
      "why": "Primary Ayurvedic herb for respiratory infections and immune support",
      "preparation": "Boil 10 fresh leaves in 200ml water for 5 minutes. Strain and drink.",
      "dosage": "Twice daily, 30 minutes after meals",
      "dosha_effect": "Pacifies Kapha and Vata doshas",
      "active_compounds": "Eugenol, rosmarinic acid, ursolic acid",
      "safety": "Generally safe. Avoid in high doses during pregnancy.",
      "classical_reference": "Charaka Samhita, Sutrasthana 4.18"
    }}
  ],
  "lifestyle_advice": "One key Ayurvedic lifestyle recommendation for these symptoms",
  "diet_tip": "One dietary recommendation from Ayurveda",
  "warning": "These are traditional Ayurvedic remedies. Please consult a qualified physician for serious medical conditions."
}}"""
        response = model.generate_content(prompt)
        result = safe_parse(response.text)
        return result
    except Exception as e:
        return {"error": f"Service unavailable: {str(e)[:80]}"}
