import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import torch
import torch.nn as nn
from app.config import settings

logger = logging.getLogger(__name__)

class ModelManager:
    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[nn.Module] = None
        self.is_loaded: bool = False
        self.load_error: Optional[str] = None
        self.checkpoint_path: Path = settings.MODEL_CHECKPOINT_PATH

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def build_architecture(self) -> nn.Module:
        """
        Builds the exact DenseNet121 architecture confirmed by all notebooks:
        - DenseNet121 base
        - classifier: nn.Linear(in_features=1024, out_features=2, bias=True)
        """
        try:
            from app.model.densenet import build_densenet121
            return build_densenet121(num_classes=2)
        except Exception:
            from torchvision.models import densenet121
            model = densenet121(weights=None)
            model.classifier = nn.Linear(in_features=1024, out_features=2, bias=True)
            return model

    def load_model(self) -> bool:
        """
        Loads the checkpoint once at startup.
        Sets to eval mode and moves to selected device.
        """
        logger.info(f"Checking model checkpoint at: {self.checkpoint_path}")

        if not self.checkpoint_path.exists():
            self.is_loaded = False
            self.load_error = (
                f"Deployment checkpoint '{self.checkpoint_path.name}' was not found at {self.checkpoint_path}. "
                "The application is in standby mode. Place the checkpoint file into backend/artifacts/model/ to enable inference."
            )
            logger.warning(self.load_error)
            return False

        try:
            logger.info("Instantiating DenseNet121 architecture...")
            model = self.build_architecture()

            logger.info(f"Loading checkpoint weights from {self.checkpoint_path} onto {self.device}...")
            state_dict = torch.load(self.checkpoint_path, map_location=self.device)

            # Some checkpoints save inside 'state_dict' or 'model_state_dict' or raw OrderedDict
            if isinstance(state_dict, dict) and "state_dict" in state_dict:
                state_dict = state_dict["state_dict"]
            elif isinstance(state_dict, dict) and "model_state_dict" in state_dict:
                state_dict = state_dict["model_state_dict"]

            # Load strictly
            model.load_state_dict(state_dict, strict=True)
            model.to(self.device)
            model.eval()

            self.model = model
            self.is_loaded = True
            self.load_error = None
            logger.info("✓ DenseNet121 model loaded successfully and set to eval mode.")
            return True

        except Exception as e:
            self.is_loaded = False
            self.model = None
            self.load_error = f"Failed to load model checkpoint: {str(e)}"
            logger.error(self.load_error, exc_info=True)
            return False

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validates model and required deployment artifacts.
        """
        artifacts_status = {
            "checkpoint_exists": self.checkpoint_path.exists(),
            "temperature_scaling_exists": settings.CALIBRATION_PATH.exists(),
            "decision_threshold_exists": settings.DECISION_THRESHOLD_PATH.exists(),
            "uncertainty_summary_exists": settings.UNCERTAINTY_PATH.exists(),
            "gradcam_methodology_exists": settings.GRADCAM_METHODOLOGY_PATH.exists(),
            "training_configuration_exists": settings.TRAINING_CONFIG_PATH.exists()
        }

        all_artifacts_present = all(artifacts_status.values())

        return {
            "model_loaded": self.is_loaded,
            "device": str(self.device),
            "architecture": "DenseNet121",
            "classifier": "Linear(in_features=1024, out_features=2, bias=True)",
            "num_classes": 2,
            "class_mapping": settings.CLASS_MAPPING,
            "input_size": "224x224x3",
            "checkpoint_path": str(self.checkpoint_path),
            "artifacts_status": artifacts_status,
            "all_artifacts_present": all_artifacts_present,
            "load_error": self.load_error
        }

model_manager = ModelManager.get_instance()
