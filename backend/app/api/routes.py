import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import Image
import io

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.database.models import AnalysisRecord
from app.model.loader import model_manager
from app.model.inference import inference_service
from app.model.calibration import temperature_scaler
from app.model.uncertainty import evaluator
from app.services.report_service import generate_pdf_report
from app.api.schemas import (
    HealthResponse, ModelInfoResponse, PredictionResponse, AnalysisDetailResponse,
    HistoryResponse, HistoryItem
)

router = APIRouter()

STANDARD_DISCLAIMER = (
    "This application is a research prototype for educational and experimental purposes. "
    "It is not a medical diagnostic device and must not be used as a substitute for evaluation by a qualified healthcare professional."
)

GRADCAM_NOTE = (
    "An interpretability visualization showing image regions that contributed to the model prediction. "
    "Does not prove disease or replace radiologist evaluation."
)

@router.get("/health", response_model=HealthResponse)
def get_health():
    """
    Task 27: Health endpoint.
    Exposes API status, model loading status, compute device, and artifact availability.
    """
    validation = model_manager.validate_configuration()
    model_loaded = validation["model_loaded"]

    if model_loaded:
        status_str = "healthy"
        msg = "DenseNet121 model and all deployment artifacts are loaded and ready."
    else:
        status_str = "standby"
        if not validation["artifacts_status"]["checkpoint_exists"]:
            msg = "Model checkpoint (best_robustness_finetuned_densenet121.pth) is awaiting supply in backend/artifacts/model/."
        else:
            msg = validation.get("load_error") or "Model failed to load."

    return HealthResponse(
        status=status_str,
        app_version=settings.VERSION,
        model_loaded=model_loaded,
        device=validation["device"],
        artifacts_status=validation["artifacts_status"],
        message=msg
    )

@router.get("/model-info", response_model=ModelInfoResponse)
def get_model_info():
    """
    Task 28: Model information endpoint.
    Returns exact architecture, calibration, threshold, uncertainty, and verified evaluation metrics.
    """
    # Ground truth metrics from Notebook 3 Cell 210
    internal_metrics = {
        "dataset": "Chest X-ray (Clean internal test split)",
        "samples": 5439,
        "accuracy": 0.9638,
        "precision": 0.9478,
        "sensitivity": 0.9816,
        "specificity": 0.9460,
        "f1_score": 0.9644,
        "roc_auc": 0.9960,
        "brier_score_calibrated": 0.0231,
        "ece_calibrated": 0.0036
    }

    external_metrics = {
        "dataset": "Kermany Pediatric Chest X-ray",
        "samples": 624,
        "training_performed_on_dataset": False,
        "accuracy": 0.9535,
        "precision": 0.9308,
        "sensitivity": 1.0000,
        "specificity": 0.8761,
        "f1_score": 0.9642,
        "roc_auc": 0.9998
    }

    return ModelInfoResponse(
        model_name="Robustness-improved DenseNet121",
        architecture="DenseNet121 with custom 2-class Linear classifier",
        target_layer="features.denseblock4",
        input_size="224 × 224",
        input_channels=3,
        preprocessing="Resize((224, 224)) -> Grayscale(num_output_channels=3) -> ToTensor() -> ImageNet Normalization",
        classes={"0": "NORMAL", "1": "PNEUMONIA"},
        temperature=temperature_scaler.temperature,
        decision_threshold=evaluator.decision_threshold,
        uncertainty_threshold=evaluator.uncertainty_threshold,
        internal_test_metrics=internal_metrics,
        external_test_metrics=external_metrics,
        calibration_method="Temperature Scaling (logits / T -> softmax)",
        decision_rule="If P(Pneumonia) >= 0.16 -> PNEUMONIA, else NORMAL",
        uncertainty_rule="If (1 - Confidence) <= 0.10 -> ACCEPTED, else UNCERTAIN / REVIEW",
        disclaimer=STANDARD_DISCLAIMER
    )

@router.post("/predict", response_model=PredictionResponse)
async def predict_xray(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Task 29: Prediction endpoint.
    Accepts an uploaded chest X-ray image (JPG/JPEG/PNG).
    Performs validation, inference, temperature scaling, thresholding, uncertainty calculation,
    real Grad-CAM generation, and records the analysis into SQLite.
    """
    # 1. Validate model readiness
    if not model_manager.is_loaded:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model is currently in standby mode. The model checkpoint "
                "'best_robustness_finetuned_densenet121.pth' was not found in backend/artifacts/model/. "
                "Please place the trained checkpoint file in backend/artifacts/model/ to run predictions."
            )
        )

    # 2. Validate file extension
    original_filename = file.filename or "uploaded_xray.png"
    ext = Path(original_filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 3. Read content & validate size
    content = await file.read()
    if not content or len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB."
        )

    # 4. Validate image readability using PIL
    try:
        pil_image = Image.open(io.BytesIO(content))
        pil_image.verify()
        # Re-open after verify() as verify() can mutate internal state
        pil_image = Image.open(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file is not a valid or readable image: {str(e)}"
        )

    # 5. Generate safe unique ID and save original image
    analysis_id = str(uuid.uuid4())
    safe_filename = f"{analysis_id}_{original_filename}"
    original_save_path = settings.UPLOADS_DIR / safe_filename
    
    # Save the readable image safely
    pil_image.save(original_save_path)

    # 6. Execute ML Inference Pipeline
    try:
        inference_result = inference_service.run_inference(pil_image, analysis_id)
    except Exception as e:
        # Cleanup uploaded file on ML failure
        if original_save_path.exists():
            original_save_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Error executing inference and Grad-CAM: {str(e)}"
        )

    # 7. Persist to SQLite Database (Task 34)
    record = AnalysisRecord(
        id=analysis_id,
        created_at=datetime.utcnow(),
        original_filename=original_filename,
        prediction=inference_result["prediction"],
        class_index=inference_result["class_index"],
        normal_probability=inference_result["normal_probability"],
        pneumonia_probability=inference_result["pneumonia_probability"],
        confidence=inference_result["confidence"],
        uncertainty=inference_result["uncertainty"],
        status=inference_result["status"],
        decision_threshold=inference_result["decision_threshold"],
        uncertainty_threshold=inference_result["uncertainty_threshold"],
        temperature=inference_result["temperature"],
        original_image_path=str(original_save_path),
        gradcam_image_path=inference_result["gradcam_path"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResponse(
        analysis_id=analysis_id,
        prediction=record.prediction,
        class_index=record.class_index,
        pneumonia_probability=record.pneumonia_probability,
        normal_probability=record.normal_probability,
        confidence=record.confidence,
        uncertainty=record.uncertainty,
        status=record.status,
        decision_threshold=record.decision_threshold,
        uncertainty_threshold=record.uncertainty_threshold,
        temperature=record.temperature,
        original_image_url=f"/static/uploads/{safe_filename}",
        gradcam_url=f"/static/gradcam/{inference_result['gradcam_filename']}",
        created_at=record.created_at.isoformat(),
        interpretability_note=GRADCAM_NOTE,
        disclaimer=STANDARD_DISCLAIMER
    )

@router.get("/history", response_model=HistoryResponse)
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Task 35: History endpoint. Returns real past analyses with pagination.
    """
    total = db.query(AnalysisRecord).count()
    records = (
        db.query(AnalysisRecord)
        .order_by(AnalysisRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for r in records:
        safe_orig_filename = f"{r.id}_{r.original_filename}"
        items.append(
            HistoryItem(
                id=r.id,
                created_at=r.created_at.isoformat(),
                original_filename=r.original_filename,
                prediction=r.prediction,
                class_index=r.class_index,
                normal_probability=round(r.normal_probability, 4),
                pneumonia_probability=round(r.pneumonia_probability, 4),
                confidence=round(r.confidence, 4),
                uncertainty=round(r.uncertainty, 4),
                status=r.status,
                original_image_url=f"/static/uploads/{safe_orig_filename}",
                gradcam_url=f"/static/gradcam/gradcam_{r.id}.png"
            )
        )

    return HistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        records=items
    )

@router.get("/history/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis_detail(analysis_id: str, db: Session = Depends(get_db)):
    """
    Task 36: Single analysis details endpoint.
    """
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")

    safe_orig_filename = f"{record.id}_{record.original_filename}"

    return AnalysisDetailResponse(
        analysis_id=record.id,
        original_filename=record.original_filename,
        prediction=record.prediction,
        class_index=record.class_index,
        pneumonia_probability=record.pneumonia_probability,
        normal_probability=record.normal_probability,
        confidence=record.confidence,
        uncertainty=record.uncertainty,
        status=record.status,
        decision_threshold=record.decision_threshold,
        uncertainty_threshold=record.uncertainty_threshold,
        temperature=record.temperature,
        original_image_url=f"/static/uploads/{safe_orig_filename}",
        gradcam_url=f"/static/gradcam/gradcam_{record.id}.png",
        created_at=record.created_at.isoformat(),
        interpretability_note=GRADCAM_NOTE,
        disclaimer=STANDARD_DISCLAIMER
    )

@router.get("/report/{analysis_id}")
def download_pdf_report(analysis_id: str, db: Session = Depends(get_db)):
    """
    Task 37: Dynamic ReportLab PDF report generation endpoint.
    """
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")

    pdf_filename = f"Pneumonia_Report_{analysis_id}.pdf"
    pdf_path = settings.REPORTS_DIR / pdf_filename

    try:
        generate_pdf_report(record.to_dict(), pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

    return FileResponse(
        path=str(pdf_path),
        filename=pdf_filename,
        media_type="application/pdf"
    )
