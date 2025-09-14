import torch
from threading import Lock
from typing import Optional

MODEL_PATH = "model_crime_ucf.pth"

class ModelLoader:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.model = None
                    cls._instance.device = None
        return cls._instance

    def load(self, model_class, model_path: Optional[str] = None, device: Optional[str] = None):
        if self.model is not None:
            return self.model
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        path = model_path or MODEL_PATH
        self.model = model_class()
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        # Warmup: dummy forward
        with torch.no_grad():
            dummy = torch.zeros((1, 3, 224, 224), device=self.device)
            _ = self.model(dummy)
        return self.model

    def get_model(self):
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        return self.model

    def get_device(self):
        return self.device

model_loader = ModelLoader()
