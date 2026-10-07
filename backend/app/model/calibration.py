import json
import logging
from pathlib import Path
import torch
import torch.nn.functional as F
from app.config import settings

logger = logging.getLogger(__name__)

class TemperatureScaler:
    def __init__(self, artifact_path: Path = None):
        self.artifact_path = artifact_path or settings.CALIBRATION_PATH
        self.temperature = self._load_temperature()

    def _load_temperature(self) -> float:
        if self.artifact_path and self.artifact_path.exists():
            try:
                with open(self.artifact_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    temp = float(data.get("temperature", settings.DEFAULT_TEMPERATURE))
                    logger.info(f"Loaded temperature {temp} from {self.artifact_path}")
                    return temp
            except Exception as e:
                logger.warning(f"Error reading temperature artifact {self.artifact_path}: {e}. Using default.")
        else:
            logger.warning(f"Temperature artifact {self.artifact_path} not found. Using default {settings.DEFAULT_TEMPERATURE}.")
        return settings.DEFAULT_TEMPERATURE

    def scale_and_softmax(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Applies temperature scaling:
        scaled_logits = logits / T
        probabilities = softmax(scaled_logits, dim=-1)
        """
        scaled_logits = logits / self.temperature
        probabilities = F.softmax(scaled_logits, dim=-1)
        return probabilities

# Singleton instance
temperature_scaler = TemperatureScaler()
