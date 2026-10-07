import os
import json
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"
STORAGE_DIR = BACKEND_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
GRADCAM_DIR = STORAGE_DIR / "gradcam"
REPORTS_DIR = STORAGE_DIR / "reports"

# Ensure storage directories exist
for d in [STORAGE_DIR, UPLOADS_DIR, GRADCAM_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pneumonia-AI-System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Model Artifact Paths
    ARTIFACTS_DIR: Path = ARTIFACTS_DIR
    MODEL_CHECKPOINT_PATH: Path = ARTIFACTS_DIR / "model" / "best_robustness_finetuned_densenet121.pth"
    CALIBRATION_PATH: Path = ARTIFACTS_DIR / "calibration" / "temperature_scaling.json"
    DECISION_THRESHOLD_PATH: Path = ARTIFACTS_DIR / "decision" / "selected_decision_threshold.json"
    UNCERTAINTY_PATH: Path = ARTIFACTS_DIR / "uncertainty" / "uncertainty_summary.json"
    GRADCAM_METHODOLOGY_PATH: Path = ARTIFACTS_DIR / "gradcam" / "gradcam_methodology.json"
    TRAINING_CONFIG_PATH: Path = ARTIFACTS_DIR / "preprocessing" / "training_configuration.csv"

    # Database
    DATABASE_URL: str = f"sqlite:///{STORAGE_DIR / 'pneumonia_ai.db'}"

    # Storage Paths
    STORAGE_DIR: Path = STORAGE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    GRADCAM_DIR: Path = GRADCAM_DIR
    REPORTS_DIR: Path = REPORTS_DIR

    # Upload validation
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png"]

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Defaults from artifacts if file loading needs fallbacks
    DEFAULT_TEMPERATURE: float = 1.0726476907730103
    DEFAULT_DECISION_THRESHOLD: float = 0.16
    DEFAULT_UNCERTAINTY_THRESHOLD: float = 0.10

    # Classes
    CLASS_NAMES: List[str] = ["NORMAL", "PNEUMONIA"]
    CLASS_MAPPING: dict = {0: "NORMAL", 1: "PNEUMONIA"}

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
