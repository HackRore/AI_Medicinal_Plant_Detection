import os
import json
import asyncio
import base64
from typing import Optional
from app.utils.json_utils import safe_parse_gemini_json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

class GeminiService:
    """Wrapper to maintain compatibility with get_gemini_service() pattern."""
    def get_plant_analysis(self, *args, **kwargs):
        return get_plant_analysis(*args, **kwargs)
    
    def chat_about_plant(self, *args, **kwargs):
        return chat_about_plant(*args, **kwargs)

_gemini_service_instance = GeminiService()

def get_gemini_service():
    return _gemini_service_instance

gemini_service = _gemini_service_instance

async def _call_gemini_text(prompt: str) -> str:
    """Call Gemini text API with timeout using google-generativeai."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
            ),
            timeout=15.0
        )
        return response.text or ""
    except asyncio.TimeoutError:
        return ""
    except Exception as e:
        print(f"Gemini text error: {e}")
        return ""

async def _call_gemini_vision(image_bytes: bytes, prompt: str) -> str:
    """Call Gemini vision API with image + prompt using google-generativeai."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Format for google-generativeai
        content = [
            {"mime_type": "image/jpeg", "data": image_bytes},
            prompt
        ]
        
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.generate_content(
                    content,
                    generation_config={"response_mime_type": "application/json"}
                )
            ),
            timeout=15.0
        )
        return response.text or ""
    except asyncio.TimeoutError:
        return ""
    except Exception as e:
        print(f"Gemini vision error: {e}")
        return ""

async def get_plant_analysis(
    plant_name: str,
    confidence: float,
    image_bytes: Optional[bytes] = None
) -> dict:
    """Get Gemini Ayurvedic analysis for identified plant."""
    if not GEMINI_AVAILABLE:
        return {"gemini_note": "AI enrichment not configured"}

    prompt = f"""You are a multi-disciplinary botanical AI expert.
Your goal is to provide a "TRIPLE-SOURCE" verification for a leaf identified as "{plant_name}".

SOURCES OF TRUTH:
1. Native Dataset: "Indian Medicinal Leaves Image Datasets"
2. Benchmark Dataset: "PlantVillage"
3. Global Diversity: "Leafsnap / Pl@ntNet"

Provide a complete Ayurvedic medicinal profile. Cross-verify the CNN prediction against these datasets.
Return ONLY raw JSON:
{{
  "confirmed_name": "{plant_name}",
  "scientific_name": "exact scientific name",
  "ayurvedic_name": "Sanskrit/Ayurvedic name",
  "family": "plant family",
  "medicinal_uses": "detailed paragraph on top 5 medicinal uses",
  "parts_used": "which parts are used medicinally",
  "preparation": "how to prepare — decoction, paste, juice etc",
  "dosage": "typical Ayurvedic dosage",
  "active_compounds": "key therapeutic compounds",
  "dosha_effect": "Ayurvedic profile",
  "toxicity": "safety info",
  "classical_reference": "Ayurvedic texts",
  "interesting_fact": "fun fact",
  "vision_note": "A final verdict after weighing the 3 datasets above. Do you agree?"
}}
"""
    if image_bytes:
        raw = await _call_gemini_vision(image_bytes, prompt)
    else:
        raw = await _call_gemini_text(prompt)

    result = safe_parse_gemini_json(raw)
    if not result:
        result = {"gemini_note": "AI enrichment unavailable — showing model result"}
    return result

async def get_symptom_recommendations(symptoms: str) -> dict:
    """Get Ayurvedic plant recommendations for given symptoms."""
    if not GEMINI_AVAILABLE:
        return {"error": "AI service not configured"}

    prompt = f"""You are a senior Ayurvedic physician. Patient describes: "{symptoms}"
Recommend exactly 3 medicinal plants. Return ONLY raw JSON:
{{
  "recommendations": [
    {{
      "plant": "Tulsi",
      "scientific_name": "Ocimum tenuiflorum",
      "ayurvedic_name": "Tulasi",
      "why": "Primary herb for respiratory infections",
      "preparation": "Boil 10 fresh leaves in 200ml water for 5 minutes.",
      "dosage": "Twice daily",
      "dosha_effect": "Pacifies Kapha and Vata",
      "active_compounds": "Eugenol",
      "safety": "Generally safe.",
      "classical_reference": "Charaka Samhita"
    }}
  ],
  "lifestyle_advice": "tip",
  "diet_tip": "tip",
  "warning": "consult a physician"
}}"""

    raw = await _call_gemini_text(prompt)
    result = safe_parse_gemini_json(raw)
    if not result or "recommendations" not in result:
        return {"error": "Could not generate recommendations."}
    return result
