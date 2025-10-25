
import torch
import numpy as np
from PIL import Image
import cv2
from typing import Dict, List
from .model_loader import model_loader, MODEL_PATH

# Load model and processor once (singleton, all local)
try:
    model = model_loader.load(model_path=MODEL_PATH)
    processor = model_loader.get_processor()
    device = model_loader.get_device()
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

def bgr_to_pil(img: np.ndarray) -> Image.Image:
    """Convert BGR frame from OpenCV to PIL Image"""
    try:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    except Exception as e:
        raise ValueError(f"Failed to convert BGR to PIL: {e}")

def predict_frame(frame: np.ndarray, top_k: int = 3) -> Dict[str, float]:
    """Predict crime class for a single frame"""
    try:
        if frame is None or frame.size == 0:
            raise ValueError("Frame is empty or None")
        
        pil_img = bgr_to_pil(frame)
        inputs = processor(images=pil_img, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        
        topk = torch.topk(probs, k=min(top_k, len(probs)))
        id2label = getattr(model.config, "id2label", None)
        if id2label is None:
            id2label = {i: str(i) for i in range(len(probs))}
        
        result = {id2label[int(idx.item())]: prob.item() for prob, idx in zip(topk.values, topk.indices)}
        return result
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")

def predict_batch(frames: List[np.ndarray], top_k: int = 3) -> List[Dict[str, float]]:
    """Predict crime classes for a batch of frames"""
    try:
        if not frames:
            return []
        
        pil_imgs = [bgr_to_pil(f) for f in frames]
        inputs = processor(images=pil_imgs, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        results = []
        id2label = getattr(model.config, "id2label", None)
        if id2label is None:
            id2label = {i: str(i) for i in range(probs.shape[1])}
        
        for p in probs:
            topk = torch.topk(p, k=min(top_k, len(p)))
            results.append({id2label[int(idx.item())]: prob.item() for prob, idx in zip(topk.values, topk.indices)})
        return results
    except Exception as e:
        raise RuntimeError(f"Batch prediction failed: {e}")
