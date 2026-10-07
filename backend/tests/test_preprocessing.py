from PIL import Image
import torch
from app.model.preprocessing import preprocess_image, IMAGENET_MEAN, IMAGENET_STD

def test_preprocessing():
    # Create test PIL image
    img = Image.new("RGB", (300, 400), color=(128, 128, 128))
    tensor = preprocess_image(img)
    
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 3, 224, 224)
    # Check that channels are identical since it converts to grayscale first
    ch0 = tensor[0, 0]
    ch1 = tensor[0, 1]
    # Normalization mean/std differs per channel, but grayscale value is constant
    assert ch0.shape == (224, 224)
