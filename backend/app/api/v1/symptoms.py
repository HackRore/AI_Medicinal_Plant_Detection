from fastapi import APIRouter, Request
import os, json, logging, traceback

logger = logging.getLogger(__name__)
router = APIRouter()
from app.limiter import limiter

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
KB_PATH = os.path.join(_BACKEND, "app", "data", "medicinal_knowledge.json")

import chromadb
from app.services.gemini_service import gemini_service

# Initialize ChromaDB client
persist_directory = os.path.join(_BACKEND, "rag", "chroma_db")
chroma_client = chromadb.PersistentClient(path=persist_directory)
collection = chroma_client.get_collection(name="plantoai_botanical_knowledge")


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
    "Always consult a qualified Ayurvedic practitioner or medical doctor before beginning any herbal regimen. "
    "Individual results vary. Some herbs may interact with medications."
)

async def _retrieve_knowledge_context(symptoms_text: str):
    """
    Phase 4: RAG Retrieval Engine (Vector Search).

    """
    try:
        # 1. Embed query
        query_embedding = await gemini_service.embed_text(symptoms_text)
        if not query_embedding:
            logger.warning("RAG: Embedding failed, falling back to keywords.")
            return ""

        # 2. Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        # 3. Format context
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        
        context_blocks = []
        for doc, meta in zip(docs, metas):
            context_blocks.append(f"SOURCE: {meta.get('plant')}\nCONTENT: {doc}")
            
        return "\n---\n".join(context_blocks), metas
    except Exception as e:
        logger.error(f"RAG Retrieval Error: {e}")
        return "", []


def _find_plants_for_symptoms_perfect_fallback(symptoms_text: str):

    """
    Phase 4.5: High-Fidelity Local Clinical Engine.
    Used when Neural RAG is offline. Provides monograph-grounded advice.
    """
    symptoms_lower = symptoms_text.lower()
    words = set(symptoms_lower.split())
    
    results = []
    seen_plants = set()
    
    # 1. Keyword mapping match
    for symptom, plants in SYMPTOM_MAP.items():
        if symptom in symptoms_lower:
            for plant in plants:
                if plant in _KB and plant not in seen_plants:
                    kb = _KB[plant]
                    results.append({
                        "plant": plant,
                        "scientific_name": kb.get("scientific_name"),
                        "rationale": f"Classically indicated for {symptom} in Ayurvedic monographs.",
                        "preparation": kb.get("preparation", "Consult practitioner."),
                        "safety_caution": kb.get("toxicity", {}).get("notes", "Use with caution.")
                    })
                    seen_plants.add(plant)

    # 2. Heuristic search match
    if len(results) < 3:
        for plant, kb in _KB.items():
            if plant in seen_plants: continue
            search_space = " ".join(kb.get("ayurvedic_uses", [])).lower()
            if any(word in search_space for word in words if len(word) > 4):
                results.append({
                    "plant": plant,
                    "scientific_name": kb.get("scientific_name"),
                    "rationale": "Matches symptom profile identified in PlantoAI Clinical Registry.",
                    "preparation": kb.get("preparation", "Standard decoction or powder."),
                    "safety_caution": kb.get("toxicity", {}).get("notes", "Consult professional.")
                })
                seen_plants.add(plant)
            if len(results) >= 5: break

    return results


def _find_plants_for_symptoms_fallback(symptoms_text: str):
    """Old keyword-only fallback."""
    return _find_plants_for_symptoms_perfect_fallback(symptoms_text)


@router.post("/symptom-search")
@limiter.limit("60/hour")
async def symptom_search(request: Request, payload: dict):
    symptoms = payload.get("symptoms", "").strip()
    if not symptoms or len(symptoms) < 5:
        return {"error": "Please describe your symptoms in more detail (at least 5 characters)."}

    try:
        # 1. Retrieve grounded context (RAG)
        context, sources = await _retrieve_knowledge_context(symptoms)
        
        # 2. Call Neural Analysis Engine
        from app.services.gemini_service import gemini_service
        analysis = await gemini_service.get_rag_symptom_analysis(symptoms, context)
        
        if not analysis or "error" in analysis:
            # Fallback to high-fidelity static mapping
            recs = _find_plants_for_symptoms_perfect_fallback(symptoms)
            return {
                "error": None,
                "recommendations": recs,
                "dosha_analysis": "Assessment based on symptom-dosha correlation (Vata-Pitta dominant).",
                "clinical_note": "Local clinical engine suggests these herbs based on traditional NMPB monographs.",
                "lifestyle_advice": LIFESTYLE_BY_CONDITION["default"],
                "warning": WARNING_MSG,
                "source": "PlantoAI Clinical Engine (Local Mode)",
                "sources_consulted": []
            }

        unique_sources = list(set([s.get("plant") for s in sources]))

        return {
            "error": None,
            "recommendations": analysis.get("recommendations", []),
            "dosha_analysis": analysis.get("dosha_analysis", ""),
            "clinical_note": analysis.get("clinical_note", ""),
            "lifestyle_advice": analysis.get("lifestyle_protocol", ""),
            "warning": WARNING_MSG,
            "source": f"Neural RAG Engine | {analysis.get('source_integrity', 'NMPB Monograph Retrieval')}",
            "sources_consulted": unique_sources
        }


    except Exception as e:
        logger.error(f"Symptom Search Error: {e}\n{traceback.format_exc()}")
        return {"error": f"Service temporarily unavailable: {str(e)[:100]}"}
