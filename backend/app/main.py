import os
os.environ.pop("DATABASE_URL", None)
os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_KEY", None)

import sys
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PlantoAI API", version="2.0")
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

logger.info("Starting PlantoAI backend...")

try:
    from app.services.ml_service import ml_service
    logger.info(f"ML service loaded: {len(ml_service.class_names)} classes")
    ML_LOADED = True
except Exception as e:
    logger.error(f"ML service failed: {e}")
    import traceback; traceback.print_exc()
    ml_service = None
    ML_LOADED = False

@app.get("/")
def root():
    return {"message": "PlantoAI API v2", "status": "online", "ml_loaded": ML_LOADED}

@app.get("/ping")
def ping():
    return {"pong": True}

@app.get("/health")
def health():
    return {
        "status": "ok" if ML_LOADED else "degraded",
        "model_loaded": ML_LOADED,
        "classes": len(ml_service.class_names) if ml_service else 0
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
    if not ML_LOADED or ml_service is None:
        raise HTTPException(503, "Model not loaded")
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    raw = await file.read()
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 15MB)")
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
            "level": "unknown", "level_code": 3,
            "notes": "Consult an Ayurvedic practitioner."
        }),
        "medicinal": {
            "description": kb.get("description", ""),
            "ayurvedic_uses": kb.get("ayurvedic_uses", []),
            "preparation": kb.get("preparation", "Consult a qualified Ayurvedic practitioner."),
            "active_compounds": kb.get("active_compounds", []),
            "contraindications": kb.get("contraindications", []),
        },
        "gradcam": result.get("gradcam", {}),
        "quality": {
            "passed": result["quality_passed"],
            "score": result["quality_score"],
            "message": "Good image" if result["quality_passed"] else
                "Low confidence. Try better lighting, single leaf, plain background."
        },
        "meta": {
            "inference_ms": result["inference_ms"],
            "model_version": "plantoai_v2"
        }
    }

@app.get("/api/v1/plants")
def list_plants(search: str = "", page: int = 1, limit: int = 20):
    if not ml_service:
        return {"plants": [], "total": 0, "page": 1, "pages": 0}
    plants = [{"scientific_name": k, **v} for k, v in ml_service.kb.items()]
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
    r = ml_service._kb(name.replace("-", " "))
    return {"scientific_name": name, **r} if r else {"error": "Not found"}
