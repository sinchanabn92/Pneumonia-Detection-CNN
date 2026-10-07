from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    status: str
    app_version: str
    model_loaded: bool
    device: str
    artifacts_status: Dict[str, bool]
    message: str

class ModelInfoResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_name: str
    architecture: str
    target_layer: str
    input_size: str
    input_channels: int
    preprocessing: str
    classes: Dict[str, str]
    temperature: float
    decision_threshold: float
    uncertainty_threshold: float
    internal_test_metrics: Dict[str, Any]
    external_test_metrics: Dict[str, Any]
    calibration_method: str
    decision_rule: str
    uncertainty_rule: str
    disclaimer: str

class PredictionResponse(BaseModel):
    analysis_id: str
    prediction: str
    class_index: int
    pneumonia_probability: float
    normal_probability: float
    confidence: float
    uncertainty: float
    status: str
    decision_threshold: float
    uncertainty_threshold: float
    temperature: float
    original_image_url: str
    gradcam_url: str
    created_at: str
    interpretability_note: str
    disclaimer: str

class AnalysisDetailResponse(PredictionResponse):
    original_filename: str

class HistoryItem(BaseModel):
    id: str
    created_at: str
    original_filename: str
    prediction: str
    class_index: int
    normal_probability: float
    pneumonia_probability: float
    confidence: float
    uncertainty: float
    status: str
    original_image_url: str
    gradcam_url: str

class HistoryResponse(BaseModel):
    total: int
    page: int
    page_size: int
    records: List[HistoryItem]
