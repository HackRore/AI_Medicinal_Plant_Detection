from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import auth, predict, plants, explain, recommend, gemini, feedback, quality_check, symptoms

# Step 7: Lifespan block
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Test DB connection on startup
    try:
        from app.db.session import test_connection
        test_connection()
    except Exception as e:
        print(f"Startup DB test error: {e}")
        
    print("PlantoAI backend started successfully")
    yield
    print("PlantoAI backend shutting down")

app = FastAPI(
    title="PlantoAI API",
    version="2.0.0",
    lifespan=lifespan,
    redirect_slashes=False  # Crucial for CORS preflight robustness
)

# Hardened Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Highly permissive for Vercel dynamic domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Health endpoint
@app.get("/health")
def health():
    from app.services.ml_service import ml_service
    status = "healthy" if ml_service.initialized else "initializing"
    return {
        "status": "ok",
        "service": "PlantoAI",
        "version": "2.0.0",
        "ml_engine": "Triple-Intelligence-v3" if getattr(ml_service, 'use_torch', False) else "ONNX-Fallback",
        "model_status": status
    }

# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(quality_check.router, prefix=f"{settings.API_V1_PREFIX}/quality-check", tags=["Quality Check"])
app.include_router(predict.router, prefix=f"{settings.API_V1_PREFIX}/predict", tags=["Prediction"])
app.include_router(plants.router, prefix=f"{settings.API_V1_PREFIX}/plants", tags=["Plants"])
app.include_router(explain.router, prefix=f"{settings.API_V1_PREFIX}/explain", tags=["Explainability"])
app.include_router(recommend.router, prefix=f"{settings.API_V1_PREFIX}/recommend", tags=["Recommendations"])
app.include_router(gemini.router, prefix=f"{settings.API_V1_PREFIX}/gemini", tags=["Gemini AI"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_PREFIX}/feedback", tags=["AI Feedback Loop"])
app.include_router(symptoms.router, prefix=f"{settings.API_V1_PREFIX}", tags=["symptoms"])

@app.get("/")
async def root():
    return {
        "message": "AI Medicinal Plant Detection API",
        "version": "2.0.0",
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
