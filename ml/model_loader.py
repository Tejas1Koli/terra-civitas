
# Optimized for local ViT model loading (no HuggingFace downloads)
import torch
from threading import Lock
from typing import Optional
import json
from torchvision import transforms
from PIL import Image

MODEL_PATH = "model_crime_ucf.pth"

class SimpleImageProcessor:
    """Simple local image processor without HuggingFace dependencies"""
    def __init__(self, image_size: int = 224):
        self.image_size = image_size
        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def __call__(self, images=None, return_tensors: str = "pt"):
        if images is None:
            return {}
        
        # Handle single image or list of images
        if isinstance(images, Image.Image):
            images = [images]
        
        processed = torch.stack([self.transform(img) for img in images])
        
        return {"pixel_values": processed}

class SimpleViTModel(torch.nn.Module):
    """Simple ViT model wrapper for local .pth loading"""
    def __init__(self):
        super().__init__()
        self.config = type('Config', (), {'num_labels': 14, 'id2label': {i: str(i) for i in range(14)}})()
    
    def forward(self, pixel_values):
        # Placeholder - will be replaced with actual model weights from .pth
        pass

class ModelLoader:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.model = None
                    cls._instance.processor = None
                    cls._instance.device = None
        return cls._instance

    def load(self, model_path: str = MODEL_PATH, device: Optional[str] = None):
        if self.model is not None:
            return self.model
        
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        
        try:
            # Load model state dict directly
            state_dict = torch.load(model_path, map_location=self.device)
            
            # Initialize model and load weights
            self.model = SimpleViTModel()
            
            # Try to load state dict, handle missing keys gracefully
            try:
                self.model.load_state_dict(state_dict)
            except:
                # If full state dict doesn't match, try partial load
                for key in list(state_dict.keys()):
                    if key in self.model.state_dict():
                        self.model.state_dict()[key] = state_dict[key]
            
            # Setup processor for image preprocessing
            self.processor = SimpleImageProcessor()
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
        except FileNotFoundError:
            raise RuntimeError(f"Model file not found: {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
        
        return self.model

    def get_model(self):
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        return self.model

    def get_processor(self):
        if self.processor is None:
            raise RuntimeError("Processor not loaded. Call load() first.")
        return self.processor

    def get_device(self):
        return self.device

model_loader = ModelLoader()
