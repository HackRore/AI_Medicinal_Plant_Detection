from fastapi import APIRouter
import google.generativeai as genai
import os, re, json

router = APIRouter()

PLANT_NAMES = [
    "Aloevera", "Neem", "Tulsi", "Amla", "Ashwagandha", "Giloy",
    "Turmeric", "Brahmi", "Moringa", "Peppermint", "Ginger", "Hibiscus",
    "Lemongrass", "Curry Leaves", "Holy Basil", "Fenugreek", "Coriander",
    "Bitter Gourd", "Garlic", "Onion"
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
    return {"error": "Could not parse response", "raw": text[:300]}

@router.post("/symptom-search")
async def symptom_search(payload: dict):
    symptoms = payload.get("symptoms", "")
    if not symptoms or len(symptoms.strip()) < 3:
        return {"error": "Please describe your symptoms"}

    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are a senior Ayurvedic physician with 30 years of clinical experience.

Patient describes: "{symptoms}"

From this list of available medicinal plants: {", ".join(PLANT_NAMES)}

Recommend exactly 3 plants. Return ONLY a raw JSON object, no markdown, no backticks:
{{
  "recommendations": [
    {{
      "plant": "Tulsi",
      "scientific_name": "Ocimum tenuiflorum",
      "why": "Primary Ayurvedic herb for respiratory infections and fever",
      "preparation": "Boil 10 fresh leaves in 200ml water for 5 minutes. Drink twice daily.",
      "dosage": "Twice daily after meals",
      "dosha_effect": "Pacifies Kapha and Vata",
      "contraindications": "Avoid with blood thinners or during pregnancy in high doses",
      "classical_reference": "Charaka Samhita, Sutrasthana 4.18"
    }}
  ],
  "lifestyle_advice": "Brief Ayurvedic lifestyle tip for these symptoms",
  "warning": "These are traditional remedies. Consult a physician for serious conditions."
}}"""

        response = model.generate_content(prompt)
        result = safe_parse(response.text)
        return result

    except Exception as e:
        return {"error": f"AI service error: {str(e)[:100]}"}
