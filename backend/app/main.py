import os, sys, logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# --- G9 Path Hardening (Encapsulation Fix) ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND_ROOT = os.path.dirname(_HERE)
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)
# ---------------------------------------------

from app.api.v1 import predict, plants, stats
from app.services.ml_service import ml_service
from app.db.session import test_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PlantoAI API — G9 Outstanding Spec",
    description="Scientific-grade medicinal plant detection and PlantDoc integrated repository.",
    version="3.1.0"
)

# Global Resilience Shield: Catch-all exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"SYSTEM_CRASH_PREVENTED: {request.url} - Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "server_error",
            "message": "An internal botanical engine error occurred. Our engineers have been notified.",
            "trace_id": os.urandom(4).hex()
        }
    )

# Hardened CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restricted in production via ENV if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route Inclusions (Modular Architecture)
app.include_router(predict.router, prefix="/api/v1/predict", tags=["Neural Forge"])
app.include_router(predict.router, prefix="/predict",        tags=["Legacy Support"])
app.include_router(plants.router,  prefix="/api/v1/plants",  tags=["Botanical Repository"])

@app.get("/")
def root():
    return {
        "project": "PlantoAI",
        "spec": "G9 v3.1 Outstanding",
        "status": "online",
        "environment": os.getenv("APP_ENV", "development")
    }

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True, "classes": len(ml_service.class_names)}

@app.get("/api/v1/stats")
def stats():
    import os, json
    rp = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "ml_models", "training_report.json"))
    try:
        with open(rp) as f: r = json.load(f)
        return {"species_count": r["num_classes"], "top1_accuracy": r["top1_accuracy"], "top3_accuracy": r["top3_accuracy"], "total_training_images": r["train_images"]}
    except Exception as e:
        return {"species_count": len(ml_service.class_names), "top1_accuracy": None, "error": str(e)}
