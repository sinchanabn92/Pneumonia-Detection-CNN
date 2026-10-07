import logging
from pathlib import Path
from typing import Tuple
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)

class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None

        self.forward_handle = self.target_layer.register_forward_hook(self._save_activation)
        self.backward_handle = self.target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate(self, input_tensor: torch.Tensor, class_index: int) -> np.ndarray:
        """
        Executes real Grad-CAM with gradients enabled.
        input_tensor: shape (1, 3, 224, 224)
        class_index: 0 or 1
        Returns: normalized 2D numpy array (224, 224) in [0, 1]
        """
        # Ensure model is in eval mode and gradients are enabled
        self.model.eval()
        self.model.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(True):
            # Forward pass
            output = self.model(input_tensor)
            score = output[0, class_index]

            # Backward pass with respect to predicted class score
            score.backward(retain_graph=False)

            # Feature activations: shape (1024, H, W)
            feature_maps = self.activations[0]
            # Gradients: shape (1024, H, W)
            grads = self.gradients[0]

            # Global average pooling of gradients
            weights = grads.mean(dim=(1, 2))  # shape (1024,)

            # Weighted sum of feature maps
            cam = torch.zeros(feature_maps.shape[1:], device=feature_maps.device)
            for k, weight in enumerate(weights):
                cam += weight * feature_maps[k]

            # Apply ReLU
            cam = F.relu(cam)

            # Normalize to [0, 1]
            cam_np = cam.detach().cpu().numpy()
            cam_min = cam_np.min()
            cam_max = cam_np.max()

            if (cam_max - cam_min) > 1e-8:
                cam_normalized = (cam_np - cam_min) / (cam_max - cam_min)
            else:
                cam_normalized = np.zeros_like(cam_np)

            # Resize to 224x224
            cam_img = Image.fromarray((cam_normalized * 255).astype(np.uint8))
            cam_resized = cam_img.resize((224, 224), Image.Resampling.BILINEAR)
            cam_final = np.array(cam_resized, dtype=np.float32) / 255.0

            return cam_final

    def close(self):
        """Remove hooks to prevent memory leaks."""
        if self.forward_handle:
            self.forward_handle.remove()
        if self.backward_handle:
            self.backward_handle.remove()


def apply_jet_colormap(cam: np.ndarray) -> np.ndarray:
    """
    Applies jet colormap mapping [0, 1] values to RGB uint8 array (224, 224, 3).
    Uses matplotlib or pure numpy fallback.
    """
    try:
        import matplotlib.pyplot as plt
        cmap = plt.get_cmap("jet")
        colored = cmap(cam)[:, :, :3]  # drop alpha, shape (224, 224, 3) in [0, 1]
        return (colored * 255).astype(np.uint8)
    except Exception:
        # Pure numpy jet colormap fallback
        r = np.clip(1.5 - np.abs(4.0 * cam - 3.0), 0.0, 1.0)
        g = np.clip(1.5 - np.abs(4.0 * cam - 2.0), 0.0, 1.0)
        b = np.clip(1.5 - np.abs(4.0 * cam - 1.0), 0.0, 1.0)
        colored = np.stack([r, g, b], axis=-1)
        return (colored * 255).astype(np.uint8)


def create_gradcam_overlay(
    original_pil: Image.Image,
    cam: np.ndarray,
    output_path: Path,
    alpha: float = 0.45
) -> Tuple[Path, Path]:
    """
    Creates:
    1. Heatmap image
    2. Blended overlay on the grayscale image
    Saves to output_path.
    """
    # Resize original to 224x224 grayscale
    orig_gray = original_pil.convert("L").resize((224, 224), Image.Resampling.BILINEAR)
    orig_rgb = orig_gray.convert("RGB")
    orig_np = np.array(orig_rgb, dtype=np.float32)

    # Colorize heatmap
    heatmap_rgb = apply_jet_colormap(cam).astype(np.float32)

    # Blend: alpha * heatmap + (1 - alpha) * original
    blended = (alpha * heatmap_rgb + (1.0 - alpha) * orig_np).clip(0, 255).astype(np.uint8)
    overlay_img = Image.fromarray(blended)

    # Save overlay
    overlay_img.save(output_path, format="PNG")
    return output_path
