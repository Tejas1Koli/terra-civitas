import torch
import numpy as np
from PIL import Image
from typing import Dict, List
from transformers import AutoImageProcessor, ViTForImageClassification
import cv2
from .model_loader import model_loader

# Load processor and model once
MODEL_NAME = "Nikeytas/google-vit-best-crime-detector"
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

# For local .pth, we need to instantiate the model and load weights
model = model_loader.load(ViTForImageClassification, device=None)
device = model_loader.get_device()

# Get class labels
labels = processor.image_mean.keys() if hasattr(processor, 'image_mean') else [str(i) for i in range(model.config.num_labels)]

def bgr_to_pil(img: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

def predict_frame(frame: np.ndarray, top_k: int = 3) -> Dict[str, float]:
    pil_img = bgr_to_pil(frame)
    inputs = processor(images=pil_img, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    topk = torch.topk(probs, k=top_k)
    id2label = getattr(model.config, "id2label", None)
    if id2label is None:
        raise ValueError("model.config.id2label is None. Please ensure the model config has id2label mapping.")
    result = {id2label[int(idx.item())]: prob.item() for prob, idx in zip(topk.values, topk.indices)}
    return result

def predict_batch(frames: List[np.ndarray], top_k: int = 3) -> List[Dict[str, float]]:
    pil_imgs = [bgr_to_pil(f) for f in frames]
    inputs = processor(images=pil_imgs, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    results = []
    id2label = getattr(model.config, "id2label", None)
    if id2label is None:
        raise ValueError("model.config.id2label is None. Please ensure the model config has id2label mapping.")
    for p in probs:
        topk = torch.topk(p, k=top_k)
        results.append({id2label[int(idx.item())]: prob.item() for prob, idx in zip(topk.values, topk.indices)})
    return results
