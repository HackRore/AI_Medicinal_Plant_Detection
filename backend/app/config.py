"""
Configuration Settings
Loads environment variables and provides application configuration
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Medicinal Plant Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    STRICT_ML_MODE: bool = False  # If True, fails if models aren't loaded instead of using mock
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./medicinal_plants.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "") # Removal of hardcoded sensitive data
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = os.getenv("ALLOWED_ORIGINS", "").split(",")
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # ML Models
    MODEL_DIR: str = "./ml_models"

    VIT_MODEL_PATH: str = "./ml_models/vit_best.onnx"
    MOBILENET_MODEL_PATH: str = "./ml_models/mobilenetv2_best.onnx"
    ENHANCED_MODEL_PATH: str = "./ml_models/enhanced_model.onnx"
    LEAF_GATE_MODEL_PATH: str = "./ml_models/leaf_gate/leaf_gate.onnx"
    # Input Gate (Leaf vs Non-Leaf)
    # If enabled and model exists, the API first checks whether the input is a leaf.
    CLASS_NAMES_PATH: str = "./ml_models/class_names_full.json"
    ENSEMBLE_WEIGHTS_PATH: str = "./ml_models/ensemble_weights.json"
    ENABLE_LEAF_GATE: bool = True
    # Probability threshold for classifying as leaf. Tune using gate evaluation.
    LEAF_GATE_THRESHOLD: float = 0.5
    # If True, the app uses more permissive thresholds for demos.
    SHOWCASE_MODE: bool = True
    
    # Google Gemini
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # AWS S3 (Optional)
    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str | None = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Pydantic v2 configuration
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Create settings instance
settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODEL_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
