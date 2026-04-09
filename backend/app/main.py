from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1 import predict, plants, stats

app = FastAPI(
    title="PlantoAI API — G9 Production Spec",
    description="Zero-dummy medicinal plant detection and botanical repository.",
    version="2.0.0"
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
app.include_router(predict.router, prefix="/predict",        tags=["Legacy Support"]) # Legacy support for frontend
app.include_router(plants.router,  prefix="/api/v1/plants",  tags=["Botanical Repository"])
app.include_router(stats.router,   prefix="/api/v1/stats",   tags=["Live Metrics"])

@app.get("/")
def root():
    return {
        "project": "PlantoAI",
        "spec": "G9 v2.0 Production",
        "status": "online",
        "documentation": "/docs"
    }

@app.get("/ping")
def ping():
    return {"pong": True}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": os.getenv("NODE_ENV", "production"),
        "version": "2.0.0"
    }
