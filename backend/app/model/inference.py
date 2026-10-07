import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image
import torch

from app.config import settings
from app.model.loader import model_manager
from app.model.preprocessing import preprocess_image
from app.model.calibration import temperature_scaler
from app.model.uncertainty import evaluator
from app.model.gradcam import GradCAM, create_gradcam_overlay

logger = logging.getLogger(__name__)

class InferenceService:
    def __init__(self):
        self.manager = model_manager
        self._gradcam = None

    def get_gradcam(self) -> GradCAM:
        if not self.manager.is_loaded or self.manager.model is None:
            raise RuntimeError("Model is not loaded. Cannot initialize Grad-CAM.")
        
        # DenseNet121 final convolutional feature layer verified in Notebook 3: features.denseblock4
        target_layer = self.manager.model.features.denseblock4
        if self._gradcam is None:
            self._gradcam = GradCAM(self.manager.model, target_layer)
        return self._gradcam

    def run_inference(
        self,
        pil_image: Image.Image,
        analysis_id: str
    ) -> Dict[str, Any]:
        """
        Executes the verified inference pipeline:
        1. Model check
        2. Preprocessing (Resize -> Grayscale(3) -> ToTensor -> ImageNet norm)
        3. Forward pass
        4. Temperature scaling (logits / T -> softmax)
        5. Decision threshold (0.16)
        6. Confidence & Uncertainty (1 - conf)
        7. Status (ACCEPTED <= 0.10 else UNCERTAIN / REVIEW)
        8. Real Grad-CAM on DenseBlock4
        9. Overlay generation
        """
        if not self.manager.is_loaded or self.manager.model is None:
            raise RuntimeError(
                "Model is not loaded. Please ensure best_robustness_finetuned_densenet121.pth "
                "is placed in backend/artifacts/model/."
            )

        device = self.manager.device
        model = self.manager.model

        # 1. Preprocess
        input_tensor = preprocess_image(pil_image).to(device)

        # 2. Forward pass with no_grad for initial probabilities
        with torch.no_grad():
            logits = model(input_tensor)
            # Temperature scaling (T = 1.0726)
            probabilities = temperature_scaler.scale_and_softmax(logits)

        normal_prob = float(probabilities[0, 0].item())
        pneumonia_prob = float(probabilities[0, 1].item())

        # Ensure probabilities strictly in [0, 1]
        normal_prob = max(0.0, min(1.0, normal_prob))
        pneumonia_prob = max(0.0, min(1.0, pneumonia_prob))

        # 3. Decision threshold & Uncertainty evaluation
        eval_result = evaluator.evaluate(normal_prob, pneumonia_prob)
        predicted_class_index = eval_result["class_index"]

        # 4. Grad-CAM generation (must run with gradients enabled!)
        gradcam_engine = self.get_gradcam()
        cam = gradcam_engine.generate(input_tensor, predicted_class_index)

        # 5. Save Grad-CAM overlay
        gradcam_filename = f"gradcam_{analysis_id}.png"
        gradcam_save_path = settings.GRADCAM_DIR / gradcam_filename
        create_gradcam_overlay(pil_image, cam, gradcam_save_path)

        return {
            "analysis_id": analysis_id,
            "prediction": eval_result["prediction"],
            "class_index": predicted_class_index,
            "normal_probability": round(normal_prob, 4),
            "pneumonia_probability": round(pneumonia_prob, 4),
            "confidence": eval_result["confidence"],
            "uncertainty": eval_result["uncertainty"],
            "status": eval_result["status"],
            "decision_threshold": eval_result["decision_threshold"],
            "uncertainty_threshold": eval_result["uncertainty_threshold"],
            "temperature": temperature_scaler.temperature,
            "gradcam_filename": gradcam_filename,
            "gradcam_path": str(gradcam_save_path)
        }

inference_service = InferenceService()
