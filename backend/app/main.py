"""
FastAPI Backend - Main Application Entry Point
AI Medicinal Plant Detection System
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import engine, Base
from app.api.v1 import auth, predict, plants, explain, recommend, gemini, feedback, quality_check, symptoms
from app.models.cache import GeminiCache # Register for metadata
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.ml_service import get_ml_service

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    # Startup
    logger.info("Starting up application...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Download model from GitHub Releases
    import os
    model_path = "ml_models/efficientnetv2_best.h5"
    if not os.path.exists(model_path):
        print("Downloading model from GitHub releases...")
        import requests
        url = "https://github.com/HackRore/AI_Medicinal_Plant_Detection/releases/download/v1.0/efficientnetv2_best.h5"
        try:
            r = requests.get(url, stream=True)
            with open(model_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Model downloaded successfully!")
        except Exception as e:
            print(f"Bypassing model download: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered medicinal plant identification via leaf image recognition. Developed by Group G9.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Process Time Middleware (Performance Tracking)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global Exception Handler (Robustness)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please contact support.", "error_code": "INTERNAL_ERROR"}
    )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

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
    """Root endpoint"""
    return {
        "message": "AI Medicinal Plant Detection API",
        "version": settings.APP_VERSION,
        "deployment_timestamp": "2026-03-25T16:05:00Z", # DEPLOYMENT MARKER
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        ml = get_ml_service()
        demo_mode = bool(getattr(ml, 'use_mock', False)) or not getattr(ml, 'models_loaded', False)
    except Exception:
        demo_mode = True

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "demo_mode": demo_mode
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
