import json
import logging
from pathlib import Path
from typing import Tuple, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class DecisionAndUncertaintyEvaluator:
    def __init__(
        self,
        threshold_path: Path = None,
        uncertainty_path: Path = None
    ):
        self.threshold_path = threshold_path or settings.DECISION_THRESHOLD_PATH
        self.uncertainty_path = uncertainty_path or settings.UNCERTAINTY_PATH
        self.decision_threshold = self._load_decision_threshold()
        self.uncertainty_threshold = self._load_uncertainty_threshold()

    def _load_decision_threshold(self) -> float:
        if self.threshold_path and self.threshold_path.exists():
            try:
                with open(self.threshold_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    thresh = float(data.get("selected_decision_threshold", settings.DEFAULT_DECISION_THRESHOLD))
                    logger.info(f"Loaded decision threshold {thresh} from {self.threshold_path}")
                    return thresh
            except Exception as e:
                logger.warning(f"Error reading decision threshold {self.threshold_path}: {e}")
        return settings.DEFAULT_DECISION_THRESHOLD

    def _load_uncertainty_threshold(self) -> float:
        if self.uncertainty_path and self.uncertainty_path.exists():
            try:
                with open(self.uncertainty_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    thresh = float(data.get("selected_uncertainty_threshold", settings.DEFAULT_UNCERTAINTY_THRESHOLD))
                    logger.info(f"Loaded uncertainty threshold {thresh} from {self.uncertainty_path}")
                    return thresh
            except Exception as e:
                logger.warning(f"Error reading uncertainty summary {self.uncertainty_path}: {e}")
        return settings.DEFAULT_UNCERTAINTY_THRESHOLD

    def evaluate(self, normal_prob: float, pneumonia_prob: float) -> Dict[str, Any]:
        """
        Calculates:
        1. Class prediction based on selected_decision_threshold (0.16)
        2. Confidence based on predicted class probability
        3. Uncertainty = 1 - confidence
        4. Status: ACCEPTED if uncertainty <= 0.10 else UNCERTAIN / REVIEW
        """
        # Task 15: Decision threshold
        if pneumonia_prob >= self.decision_threshold:
            prediction = "PNEUMONIA"
            class_index = 1
            confidence = pneumonia_prob
        else:
            prediction = "NORMAL"
            class_index = 0
            confidence = normal_prob

        # Task 17: Uncertainty
        uncertainty = 1.0 - confidence

        # Task 18: Separate prediction and status
        if uncertainty <= self.uncertainty_threshold:
            status = "ACCEPTED"
        else:
            status = "UNCERTAIN / REVIEW"

        return {
            "prediction": prediction,
            "class_index": class_index,
            "confidence": round(confidence, 4),
            "uncertainty": round(uncertainty, 4),
            "status": status,
            "decision_threshold": self.decision_threshold,
            "uncertainty_threshold": self.uncertainty_threshold
        }

evaluator = DecisionAndUncertaintyEvaluator()
