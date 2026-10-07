from PIL import Image
import torch
import numpy as np

# ImageNet normalization statistics confirmed by all notebooks & artifacts
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def get_inference_transform():
    """
    Standard torchvision transform matching Notebooks 1, 2, and 3:
    Resize(224, 224) -> Grayscale(num_output_channels=3) -> ToTensor() -> Normalize(ImageNet)
    """
    try:
        from torchvision import transforms
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
    except ImportError:
        # Fallback transform using pure PIL and torch if torchvision is absent
        return None

def preprocess_image(pil_image: Image.Image) -> torch.Tensor:
    """
    Preprocess a PIL image to a (1, 3, 224, 224) tensor using exact ImageNet normalization.
    """
    transform = get_inference_transform()
    if transform is not None:
        tensor = transform(pil_image)
        return tensor.unsqueeze(0)
    
    # Pure PIL/Torch fallback
    # 1. Resize to 224x224
    img_resized = pil_image.resize((224, 224), Image.Resampling.BILINEAR)
    
    # 2. Grayscale to 1 channel, then duplicate across 3 channels
    img_gray = img_resized.convert("L")
    img_np = np.array(img_gray, dtype=np.float32) / 255.0  # (224, 224)
    img_3ch = np.stack([img_np, img_np, img_np], axis=0)   # (3, 224, 224)
    
    # 3. ImageNet Normalization: (x - mean) / std
    mean = np.array(IMAGENET_MEAN, dtype=np.float32)[:, None, None]
    std = np.array(IMAGENET_STD, dtype=np.float32)[:, None, None]
    norm_np = (img_3ch - mean) / std
    
    tensor = torch.from_numpy(norm_np).float()
    return tensor.unsqueeze(0)  # (1, 3, 224, 224)
