import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.v1 import predict, plants, stats, symptoms, auth, feedback
from app.limiter import limiter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neural Service Orchestration
ml_service = None
ML_LOADED = False

try:
    from app.services.ml_service import ml_service
    logger.info(f"Clinical core initialized: {len(ml_service.class_names)} validated taxa")
    ML_LOADED = True
except Exception as e:
    logger.error(f"Core synthesis failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if ml_service:
        logger.info("Lifespan: ML Service initialized.")
    yield

app = FastAPI(
    title="PlantoAI API",
    version="3.1.0",
    description="Professional Medicinal Plant Identification & Ayurvedic Intelligence",
    lifespan=lifespan
)

app.state.limiter = limiter

def rate_limit_custom_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Rate limit exceeded. Please wait before making another request."}
    )

app.add_exception_handler(RateLimitExceeded, rate_limit_custom_handler)

# CORS Configuration - Hardened for G9 Production
origins = [
    "https://plantoai.vercel.app",
    "https://phytoai.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
    "http://0.0.0.0:3000",
    "http://0.0.0.0:3001",
]

# CORS Configuration - Fully Permissive for Global Production & Team Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(predict.router, prefix="/predict", tags=["Identification"])
app.include_router(predict.router, prefix="/api/v1/predict", tags=["Identification"]) # Compatibility
app.include_router(plants.router, prefix="/api/v1/plants", tags=["Knowledge Base"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["System"])
app.include_router(symptoms.router, prefix="/api/v1", tags=["Intelligence"]) # /api/v1/symptom-search
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Security"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])  # Sprint 5: Active Learning

@app.get("/")
def root():
    return {
        "message": "PlantoAI Monolith v3.1.0 — G9 Production Spec",
        "status": "online",
        "ml_loaded": ML_LOADED,
        "engine": "EfficientNetV2-S"
    }

@app.get("/health")
def health():
    return {
        "status": "synchronized" if (ML_LOADED and ml_service and ml_service.class_names) else "degraded",
        "telemetry": {
            "neural_monolith": ml_service.model_loaded if ml_service else False,
            "botanical_kb": len(ml_service.kb) > 0 if ml_service else False,
        },
        "registry": len(ml_service.class_names) if ml_service else 0,
        "mode": "Global Production"
    }

@app.get("/ping")
def ping():
    return {"pong": True}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc}")
    response = JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred during neural processing.", "detail": str(exc)},
    )
    # Manually inject CORS headers for error responses to prevent browser masking
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
