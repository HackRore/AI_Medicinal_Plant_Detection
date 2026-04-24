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
    APP_NAME: str = "PlantoAI — G9 Outstanding Spec"
    APP_VERSION: str = "3.1.0"
    DEBUG: bool = False
    STRICT_ML_MODE: bool = True  # Production strictness
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
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
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # ML Models
    # Use absolute paths to prevent CWD dependency issues on Render
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR: str = os.path.join(BASE_DIR, "ml_models")
    PRODUCTION_MODEL_PATH: str = os.path.join(MODEL_DIR, "plantoai_model.onnx")
    CLASS_NAMES_PATH: str = os.path.join(BASE_DIR, "app", "data", "class_names.json")
    
    # Optimized Gates
    ENABLE_LEAF_GATE: bool = False # Integrated in main model for v3.1
    LEAF_GATE_THRESHOLD: float = 0.5
    # If True, the app uses more permissive thresholds for demos.
    SHOWCASE_MODE: bool = True
    
    # Google Gemini
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # AWS S3 (Optional)
    USE_S3: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = os.path.join(BASE_DIR, "logs", "app.log")
    
    # Pydantic v2 configuration
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Create settings instance
settings = Settings()

# Create necessary directories with safety
try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
except Exception as e:
    print(f"Directory creation warning: {e}")
