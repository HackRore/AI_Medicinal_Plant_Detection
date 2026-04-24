import os
# Environment Handshake Complete

import sys
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cloud DB Init
from supabase import create_client, Client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None

# Neural Service Orchestration
ml_service = None
INTEGRITY_CHECK = False
ML_LOADED = False

try:
    from app.services.ml_service import ml_service
    logger.info(f"Clinical core initialized: {len(ml_service.class_names)} validated taxa")
    INTEGRITY_CHECK = True
    ML_LOADED = True
except Exception as e:
    logger.error(f"Core synthesis failed: {e}")
    import traceback; traceback.print_exc()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Trigger background neural load (If metadata worked)
    if ml_service:
        logger.info("Lifespan: ML Service initialized.")
    yield
    # Shutdown logic (none needed)

app = FastAPI(title="PlantoAI API", version="2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

logger.info("Starting PlantoAI backend server...")

@app.get("/")
def root():
    return {"message": "PlantoAI API v2", "status": "online", "ml_loaded": ML_LOADED}

@app.get("/ping")
def ping():
    return {"pong": True}

@app.get("/health")
def health():
    return {
        "status": "synchronized" if (INTEGRITY_CHECK and ml_service and ml_service.class_names) else "degraded",
        "telemetry": {
            "neural_monolith": ml_service.model_loaded if ml_service else False,
            "botanical_kb": len(ml_service.kb) > 0 if ml_service else False,
        },
        "registry": len(ml_service.class_names) if ml_service else 0,
        "mode": "Global Production" if (ml_service and ml_service.model_loaded) else "Initial Synthesis"
    }

@app.get("/api/v1/stats")
def stats():
    rp = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "ml_models", "training_report.json"))
    try:
        with open(rp) as f:
            r = json.load(f)
        return {
            "species_count": r["num_classes"],
            "top1_accuracy": r["top1_accuracy"],
            "top3_accuracy": r["top3_accuracy"],
            "total_training_images": r["train_images"]
        }
    except Exception as e:
        return {
            "species_count": len(ml_service.class_names) if ml_service else 0,
            "top1_accuracy": None,
            "error": str(e)
        }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    raw = await file.read()
    if len(raw) > 15*1024*1024:
        raise HTTPException(400, "Max 15MB.")
    result = ml_service.predict(raw)
    if not result.get("success"):
        return JSONResponse(result)
    kb = result.get("knowledge", {})
    return {
        "success": True,
        "plant": {
            "name": (kb.get("common_names") or [result["class_name"]])[0],
            "scientific_name": kb.get("scientific_name", result["class_name"]),
            "family": kb.get("family", ""),
            "native_region": kb.get("native_region", ""),
        },
        "prediction": {
            "confidence": result["confidence_pct"],
            "confidence_label": result["confidence_label"],
            "top3": result["top3"],
        },
        "toxicity": kb.get("toxicity", {
            "level":"unknown","level_code":3,
            "notes":"Consult an Ayurvedic practitioner."
        }),
        "medicinal": {
            "description":      kb.get("description",""),
            "ayurvedic_uses":   kb.get("ayurvedic_uses",[]),
            "preparation":      kb.get("preparation",
                "Consult a qualified Ayurvedic practitioner."),
            "active_compounds": kb.get("active_compounds",[]),
            "contraindications":kb.get("contraindications",[]),
        },
        "gradcam": result.get("gradcam",{}),
        "quality": {
            "passed":  result["quality_passed"],
            "score":   result["quality_score"],
            "message": "Good image" if result["quality_passed"] else
                "Low confidence. Try better lighting, single leaf, plain background."
        },
        "meta": {
            "inference_ms": result["inference_ms"],
            "model_version": "plantoai_v2_46class"
        }
    }

@app.get("/api/v1/plants")
def list_plants(search: str = "", page: int = 1, limit: int = 20):
    if not ml_service:
        return {"plants": [], "total": 0, "page": 1, "pages": 0}
    
    plants = []
    for k, v in ml_service.kb.items():
        # Dynamic Botanical Visual Synthesis
        img_url = v.get("image_url")
        if not img_url:
            # Curated Botanical Photo IDs (strictly medicinal/plant focused)
            botanical_ids = [
                "photo-1520302630591-fd1c66ed11a8", # Aloe
                "photo-1466692476868-aef1dfb1e735", # Herbs
                "photo-1533038590840-1cde6e668a91", # Leaves
                "photo-1501004318641-72e54e3f81d4", # Greenhouse
                "photo-1518531933037-91b2f5f229cc", # Fern
                "photo-1515523110800-9415d13b84a8", # Mint
                "photo-1502672260266-1c1ef2d93688", # Botanical
                "photo-1459156212016-c812468e2115"  # Close-up
            ]
            # Select ID based on the plant's name hash for consistency
            photo_id = botanical_ids[hash(k) % len(botanical_ids)]
            img_url = f"https://images.unsplash.com/{photo_id}?q=80&w=2670&auto=format&fit=crop"
        
        plants.append({
            "scientific_name": k,
            "image_url": img_url,
            **v
        })
        
    if search:
        plants = [p for p in plants
                  if search.lower() in p["scientific_name"].lower()
                  or any(search.lower() in cn.lower()
                         for cn in p.get("common_names", []))]
    total = len(plants)
    start = (page - 1) * limit
    return {
        "plants": plants[start:start + limit],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@app.get("/api/v1/plants/{name}")
def get_plant(name: str):
    if not ml_service:
        return {"error": "Service unavailable"}
    
    # 1. Try Cloud Discovery (Supabase)
    if supabase:
        try:
            res = supabase.table("medicinal_plants").select("*").eq("scientific_name", name.replace("-", " ")).execute()
            if res.data:
                logger.info(f"Cloud Match: Found {name} in Supabase.")
                return {"source": "cloud", **res.data[0]}
        except Exception as e:
            logger.warning(f"Cloud DB bypassed: {e}")

    # 2. Fallback to Local Intelligence (JSON)
    r = ml_service._kb(name.replace("-", " "))
    return {"source": "local", "scientific_name": name, **r} if r else {"error": "Not found"}

@app.get("/api/v1/search")
def search_symptoms(query: str = ""):
    """Novelty Claim: Symptom-to-Plant Engine"""
    if not query or len(query) < 2:
        return {"results": []}
    
    query = query.lower()
    results = []
    
    # Access knowledge directly from ml_service
    if not ml_service or not ml_service.kb:
        return {"results": []}
        
    for species, info in ml_service.kb.items():
        # Match keywords in uses, description, and scientific name
        uses_match = any(query in use.lower() for use in info.get("ayurvedic_uses", []))
        desc_match = query in info.get("description", "").lower()
        name_match = query in species.lower()
        
        if uses_match or desc_match or name_match:
            results.append({
                "name": species,
                "common_names": info.get("common_names", []),
                "scientific_name": info.get("scientific_name", ""),
                "primary_use": info.get("ayurvedic_uses", [""])[0],
                "toxicity_level": info.get("toxicity", {}).get("level", "unknown"),
                "family": info.get("family", "")
            })
            
    return {"results": results, "query": query, "count": len(results)}

@app.post("/api/v1/symptom-search")
async def symptom_search(request: dict = Body(...)):
    """
    Novelty Claim: AI Ayurvedic Physician
    Performs deep-reasoning to map symptoms to medicinal plants.
    - Uses Gemini if available for personalized advice.
    - Falls back to local clinical knowledge for reliability.
    """
    symptoms = request.get("symptoms", "")
    if not symptoms or len(symptoms) < 5:
        return {"error": "Please provide a more detailed description of your symptoms."}

    try:
        from app.services.gemini_service import get_symptom_recommendations
        
        # 1. Attempt High-End AI Reasoning (Gemini)
        result = await get_symptom_recommendations(symptoms)
        
        # 2. Heuristic Fallback if Gemini is not configured or fails
        if "error" in result:
            query = symptoms.lower()
            recs = []
            
            # Simple keyword matching across our hardened Knowledge Base
            if ml_service and ml_service.kb:
                for species, info in ml_service.kb.items():
                    match_count = sum(1 for use in info.get("ayurvedic_uses", []) if query in use.lower())
                    if match_count > 0:
                        recs.append({
                            "plant": species,
                            "scientific_name": info.get("scientific_name", ""),
                            "ayurvedic_name": info.get("common_names", [""])[0],
                            "why": info.get("description", "")[:150] + "...",
                            "preparation": info.get("preparation", ""),
                            "dosage": "As per Ayurvedic practitioner guidance.",
                            "dosha_effect": "Consult clinical monograph.",
                            "safety": info.get("toxicity", {}).get("notes", "Safe"),
                            "classical_reference": info.get("references", ["API Vol I"])[0],
                            "rank": len(recs) + 1
                        })
            
            if not recs:
                return {"error": "No specific matches found in the clinical database. Please be more specific."}

            return {
                "recommendations": recs[:3],
                "lifestyle_advice": "Maintain a balanced diet (Ahara) and regular daily routine (Dinacharya).",
                "diet_tip": "Prefer warm, freshly cooked meals with mild spices like ginger and cumin.",
                "warning": "This is an automated finding. Always consult a qualified physician before starting treatment."
            }
            
        return result
        
    except Exception as e:
        return {"error": f"Search logic failed: {str(e)}"}
