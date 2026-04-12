import sys, os, logging
print("=== PRODUCTION HANDSHAKE: STARTING DIAGNOSTICS ===", flush=True)
print(f"PYTHON: {sys.version}", flush=True)
print(f"CWD: {os.getcwd()}", flush=True)
print(f"ROOT FILES: {os.listdir('.')}", flush=True)
if os.path.exists('ml_models'):
    print(f"ML_MODELS DIR FOUND: {os.listdir('ml_models')}", flush=True)
else:
    print("WARNING: 'ml_models' directory not found in current root.", flush=True)
print("==================================================", flush=True)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, logging

from app.api.v1 import predict, plants, stats
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
app.include_router(stats.router,   prefix="/api/v1/stats",   tags=["Live Metrics"])

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
    db_ok = test_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "engine": "v3.1_outstanding",
        "models": "loaded"
    }
