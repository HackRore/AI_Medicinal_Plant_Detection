import os
import re
import json
import asyncio
import base64
from typing import Optional

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

def safe_parse_json(text: str) -> dict:
    """Robust JSON parser — never crashes."""
    if not text:
        return {}
    cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', text).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}

async def _call_gemini_text(prompt: str) -> str:
    """Call Gemini text API with timeout."""
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=12.0
        )
        return response.text or ""
    except asyncio.TimeoutError:
        return ""
    except Exception as e:
        print(f"Gemini text error: {e}")
        return ""

async def _call_gemini_vision(image_bytes: bytes, prompt: str) -> str:
    """Call Gemini vision API with image + prompt."""
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg"
                        ),
                        prompt
                    ]
                )
            ),
            timeout=12.0
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
    """
    Get Gemini Ayurvedic analysis for identified plant.
    Falls back gracefully if Gemini unavailable.
    """
    if not GEMINI_AVAILABLE:
        return {"gemini_note": "AI enrichment not configured"}

    prompt = f"""You are a senior Ayurvedic physician and botanist.
A computer vision model identified this plant as: "{plant_name}" with {confidence*100:.0f}% confidence.

Provide a complete Ayurvedic medicinal profile. Return ONLY raw JSON — no markdown, no backticks, no explanation:
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
  "dosha_effect": "which doshas it pacifies or aggravates",
  "toxicity": "safety information and contraindications",
  "classical_reference": "reference from Charaka Samhita or Sushruta Samhita if applicable",
  "interesting_fact": "one surprising fact about this plant",
  "vision_note": "your own visual assessment of the image — do you agree with the CNN identification?"
}}

If you disagree with the identification based on the image, state your correction in vision_note.
CRITICAL: Always return valid JSON even if uncertain."""

    if image_bytes:
        raw = await _call_gemini_vision(image_bytes, prompt)
    else:
        raw = await _call_gemini_text(prompt)

    result = safe_parse_json(raw)
    if not result:
        result = {"gemini_note": "AI enrichment unavailable — showing model result"}
    return result

async def get_symptom_recommendations(symptoms: str) -> dict:
    """Get Ayurvedic plant recommendations for given symptoms."""
    if not GEMINI_AVAILABLE:
        return {"error": "AI service not configured"}

    prompt = f"""You are a senior Ayurvedic physician with 30 years of experience.

Patient describes: "{symptoms}"

Recommend exactly 3 medicinal plants. Return ONLY raw JSON, no markdown:
{{
  "recommendations": [
    {{
      "plant": "Tulsi",
      "scientific_name": "Ocimum tenuiflorum",
      "ayurvedic_name": "Tulasi",
      "why": "Primary herb for respiratory infections in Ayurveda",
      "preparation": "Boil 10 fresh leaves in 200ml water for 5 minutes. Drink warm.",
      "dosage": "Twice daily, 30 minutes after meals",
      "dosha_effect": "Pacifies Kapha and Vata",
      "active_compounds": "Eugenol, rosmarinic acid, ursolic acid",
      "safety": "Generally safe. Avoid in high doses during pregnancy.",
      "classical_reference": "Charaka Samhita, Sutrasthana 4.18"
    }}
  ],
  "lifestyle_advice": "One key Ayurvedic lifestyle tip for these symptoms",
  "diet_tip": "One Ayurvedic dietary recommendation",
  "warning": "These are traditional remedies. Consult a qualified physician for serious conditions."
}}"""

    raw = await _call_gemini_text(prompt)
    result = safe_parse_json(raw)
    if not result or "recommendations" not in result:
        return {"error": "Could not generate recommendations. Please try again."}
    return result
