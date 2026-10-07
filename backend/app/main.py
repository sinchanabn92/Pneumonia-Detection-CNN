import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.session import init_db
from app.model.loader import model_manager
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pneumonia_ai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("=" * 60)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info("=" * 60)
    
    # 1. Initialize SQLite Database
    logger.info("Initializing SQLite database tables...")
    init_db()
    logger.info("✓ Database initialized.")

    # 2. Load DenseNet121 model ONCE at startup (Task 22)
    logger.info("Initializing DenseNet121 model loader...")
    model_loaded = model_manager.load_model()
    if model_loaded:
        logger.info("✓ Model is loaded and ready for real inference.")
    else:
        logger.warning("! Model is in standby mode. Checkpoint file pending.")

    yield

    # Shutdown sequence
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")

app = FastAPI(
    title="Pneumonia-AI-System API",
    description="Research Prototype REST API for Pneumonia Detection from Chest X-Rays using DenseNet121, Calibration, Decision Thresholding, Uncertainty Estimation, and DenseBlock4 Grad-CAM.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware (Task 49)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static storage for image access (Task 50)
app.mount("/static/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/static/gradcam", StaticFiles(directory=str(settings.GRADCAM_DIR)), name="gradcam")

# Global Exception Handler (Task 32, 51)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check backend logs for details."}
    )

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)  # Also expose at root /health, /model-info, etc.

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health",
        "model_info_url": "/model-info"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
