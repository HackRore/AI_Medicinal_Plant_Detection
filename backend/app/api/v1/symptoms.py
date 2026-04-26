from fastapi import APIRouter
import os, json, logging, traceback

logger = logging.getLogger(__name__)
router = APIRouter()

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
KB_PATH = os.path.join(_BACKEND, "app", "data", "medicinal_knowledge.json")

# Load knowledge base once at startup
_KB = {}
try:
    with open(KB_PATH, encoding="utf-8") as f:
        _KB = json.load(f)
except Exception as e:
    logger.error(f"KB load failed: {e}")

# Symptom → plant keyword mapping (Ayurvedic clinical mapping)
SYMPTOM_MAP = {
    "fever": ["Tulsi", "Neem", "Giloy", "Chinar", "Guduchi"],
    "cough": ["Tulsi", "Vasaka", "Mulethi", "Ginger", "Pippali"],
    "cold": ["Tulsi", "Ginger", "Pippali", "Mulethi"],
    "headache": ["Ashwagandha", "Brahmi", "Shankhpushpi", "Peppermint"],
    "stress": ["Ashwagandha", "Brahmi", "Shankhpushpi", "Tulsi"],
    "anxiety": ["Brahmi", "Ashwagandha", "Shankhpushpi"],
    "skin": ["Neem", "Aloe Vera", "Turmeric", "Chandan"],
    "digestion": ["Ginger", "Bael", "Triphala", "Pippali", "Fennel"],
    "stomach": ["Bael", "Ginger", "Tulsi", "Peppermint"],
    "diabetes": ["Karela", "Bael", "Jamun", "Fenugreek", "Guduchi"],
    "joint": ["Shallaki", "Nirgundi", "Turmeric", "Guggul"],
    "pain": ["Turmeric", "Nirgundi", "Shallaki", "Ashwagandha"],
    "heart": ["Arjun", "Pushkarmool", "Guggul"],
    "blood pressure": ["Arjun", "Ashwagandha", "Sarpagandha"],
    "immunity": ["Tulsi", "Giloy", "Ashwagandha", "Amalaki"],
    "memory": ["Brahmi", "Shankhpushpi", "Ashwagandha"],
    "sleep": ["Ashwagandha", "Brahmi", "Jatamansi"],
    "fatigue": ["Ashwagandha", "Shatavari", "Tulsi", "Amalaki"],
    "liver": ["Kalmegh", "Guduchi", "Bhumyamalaki"],
    "kidney": ["Punarnava", "Gokshura", "Varuna"],
    "hair": ["Bhringraj", "Amalaki", "Brahmi"],
    "respiratory": ["Vasaka", "Pippali", "Tulsi", "Mulethi"],
    "infection": ["Neem", "Turmeric", "Giloy", "Tulsi"],
    "inflammation": ["Turmeric", "Shallaki", "Nirgundi", "Guduchi"],
    "cholesterol": ["Arjun", "Guggul", "Garlic"],
    "weight": ["Guggul", "Triphala", "Vrikshamla"],
    "weakness": ["Ashwagandha", "Shatavari", "Amalaki"],
    "acidity": ["Amalaki", "Shatavari", "Yashtimadhu"],
    "constipation": ["Triphala", "Bael", "Isabgol"],
    "diarrhea": ["Bael", "Kutaj", "Pomegranate"],
    "malaria": ["Alstonia Scholaris", "Neem", "Kalmegh"],
    "asthma": ["Vasaka", "Pippali", "Tulsi", "Pushkarmool"],
    "wound": ["Turmeric", "Aloe Vera", "Neem"],
}

LIFESTYLE_BY_CONDITION = {
    "fever": "Rest completely, drink warm water with Tulsi and ginger decoction every 3-4 hours. Avoid cold drinks and heavy food. Maintain hydration.",
    "cough": "Inhale steam with Tulsi leaves twice daily. Avoid cold foods, dairy, and exposure to smoke. Perform pranayama breathing when possible.",
    "stress": "Practice 15 minutes of Anulom Vilom (alternate nostril breathing) daily. Reduce screen time after sunset. Walk barefoot on grass for 10 minutes each morning.",
    "digestion": "Eat meals at fixed times. Walk 10 minutes after every meal. Avoid raw, cold, and processed food. Chew food thoroughly — at least 20 times per bite.",
    "default": "Follow a dinacharya (daily routine): wake before sunrise, practice light yoga or walking, eat warm cooked food, and sleep before 10pm. Consistency is key in Ayurvedic healing."
}

DIET_BY_CONDITION = {
    "fever": "Light khichdi (rice and lentil porridge) with turmeric and ghee. Warm soups. Avoid heavy proteins, oily foods, and dairy.",
    "cough": "Warm turmeric milk at bedtime. Ginger tea with honey. Avoid cold drinks, ice cream, and curd.",
    "stress": "Warm milk with Ashwagandha and saffron at night. Fresh fruits in the morning. Avoid caffeine and alcohol.",
    "digestion": "Eat ginger pickle before meals. Buttermilk with cumin and rock salt after lunch. Avoid maida, fried food, and excess sugar.",
    "default": "Prefer warm, freshly cooked meals (sattvic diet). Include ghee, turmeric, and cumin in daily cooking. Drink warm water throughout the day. Avoid reheated, processed, or cold foods."
}

WARNING_MSG = (
    "This analysis is generated from Ayurvedic classical texts for educational purposes only. "
    "PlantoAI is NOT a substitute for professional medical advice, diagnosis, or treatment. "
    "Always consult a qualified Ayurvedic practitioner or medical doctor before beginning any herbal regimen. "
    "Individual results vary. Some herbs may interact with medications."
)


def _find_plants_for_symptoms(symptoms_text: str):
    """Match symptoms to plants using keyword mapping + knowledge base."""
    symptoms_lower = symptoms_text.lower()
    scored = {}
    
    matched_condition = "default"
    
    for keyword, plants in SYMPTOM_MAP.items():
        if keyword in symptoms_lower:
            matched_condition = keyword
            for plant in plants:
                scored[plant] = scored.get(plant, 0) + 1
    
    # Sort by score, highest first
    ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
    
    results = []
    for plant_name, score in ranked[:5]:
        # Try to find data in KB (handles partial name matches)
        kb_data = None
        for kb_key in _KB.keys():
            if plant_name.lower() in kb_key.lower() or kb_key.lower() in plant_name.lower():
                kb_data = _KB[kb_key]
                break
        
        if kb_data:
            uses = kb_data.get("ayurvedic_uses", ["General wellness support"])
            rec = {
                "rank": len(results) + 1,
                "plant": plant_name,
                "scientific_name": kb_data.get("scientific_name", "—"),
                "ayurvedic_name": kb_data.get("common_names", [plant_name])[0],
                "why": uses[0] if uses else "Ayurvedic classical herb for this condition.",
                "dosha_effect": "Balances Vata-Pitta-Kapha (Tridoshic)" if score >= 2 else "Reduces Pitta and Vata",
                "safety": kb_data.get("toxicity", {}).get("notes", "Consult practitioner before use."),
                "preparation": kb_data.get("preparation", "Consult an Ayurvedic practitioner for dosage."),
                "dosage": "Follow practitioner guidance. Typical: 3-5g powder or 50ml decoction twice daily.",
                "classical_reference": kb_data.get("references", ["Ayurvedic Pharmacopoeia of India"])[0]
            }
            results.append(rec)
    
    # Fallback if no KB match found but we have ranked plants
    if not results and ranked:
        for plant_name, score in ranked[:3]:
            results.append({
                "rank": len(results) + 1,
                "plant": plant_name,
                "scientific_name": "—",
                "ayurvedic_name": plant_name,
                "why": f"Classically recommended for {symptoms_text[:50]} in Ayurvedic texts.",
                "dosha_effect": "Reduces Pitta and Vata",
                "safety": "Consult a qualified Ayurvedic practitioner before use.",
                "preparation": "Consult an Ayurvedic practitioner for correct preparation and dosage.",
                "dosage": "As directed by practitioner.",
                "classical_reference": "Ayurvedic Pharmacopoeia of India"
            })
    
    return results, matched_condition


@router.post("/symptom-search")
async def symptom_search(payload: dict):
    symptoms = payload.get("symptoms", "").strip()
    if not symptoms or len(symptoms) < 5:
        return {"error": "Please describe your symptoms in more detail (at least 5 characters)."}

    try:
        recommendations, matched_condition = _find_plants_for_symptoms(symptoms)

        if not recommendations:
            return {
                "error": None,
                "recommendations": [],
                "lifestyle_advice": LIFESTYLE_BY_CONDITION["default"],
                "diet_tip": DIET_BY_CONDITION["default"],
                "warning": WARNING_MSG,
                "source": "PlantoAI Ayurvedic Knowledge Base"
            }

        lifestyle = LIFESTYLE_BY_CONDITION.get(matched_condition, LIFESTYLE_BY_CONDITION["default"])
        diet = DIET_BY_CONDITION.get(matched_condition, DIET_BY_CONDITION["default"])

        return {
            "error": None,
            "recommendations": recommendations,
            "lifestyle_advice": lifestyle,
            "diet_tip": diet,
            "warning": WARNING_MSG,
            "source": "PlantoAI Ayurvedic Knowledge Base (Clinical Monograph Engine)"
        }

    except Exception as e:
        logger.error(f"Symptom Search Error: {e}\n{traceback.format_exc()}")
        return {"error": f"Service temporarily unavailable: {str(e)[:100]}"}
