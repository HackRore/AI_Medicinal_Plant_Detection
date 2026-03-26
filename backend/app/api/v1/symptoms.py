from fastapi import APIRouter
import google.generativeai as genai
import os, re, json, logging, traceback
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Gemini at module level
def init_gemini():
    try:
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        logger.error(f"Gemini Init Error: {e}")
    return None

model = init_gemini()

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
    global model
    symptoms = payload.get("symptoms", "").strip()
    if not symptoms:
        return {"error": "Please describe your symptoms"}
        
    try:
        if model is None:
            model = init_gemini()
            if model is None:
                return {"error": "Gemini API key not configured"}

        prompt = f"""You are a senior Ayurvedic physician.
A patient describes: "{symptoms}"
From this list only: {", ".join(AVAILABLE_PLANTS)}
Recommend exactly 3 plants. Return ONLY raw JSON:
{{
  "recommendations": [
    {{
      "plant": "Tulsi",
      "scientific_name": "Ocimum tenuiflorum",
      "ayurvedic_name": "Tulasi",
      "why": "Brief reason",
      "preparation": "How to prepare",
      "dosage": "Suggested dosage",
      "dosha_effect": "Effect on doshas",
      "active_compounds": "Key compounds",
      "safety": "Safety notes",
      "classical_reference": "Reference"
    }}
  ],
  "lifestyle_advice": "One tip",
  "diet_tip": "One tip",
  "warning": "Medical disclaimer"
}}"""
        # USE ASYNC GENERATION
        response = await model.generate_content_async(prompt, request_options={"timeout": 60})
        result = safe_parse(response.text)
        return result
    except Exception as e:
        err_msg = traceback.format_exc()
        logger.error(f"Gemini Route Error: {err_msg}")
        print(f"DEBUG: Gemini Error Traceback:\n{err_msg}")
        
        message = str(e)
        if "404" in message:
            return {"error": "AI model not found. This key might not have access to gemini-1.5-flash."}
        return {"error": f"Service unavailable: {message[:100]}"}
