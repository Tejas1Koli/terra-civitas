from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class FrameRequest(BaseModel):
    image_url: Optional[str] = None

@router.post("/predict/frame")
def predict_frame(file: UploadFile = File(None), req: FrameRequest = None):
    """Predict crime in a single frame."""
    # TODO: Implement frame prediction
    return {"label": "theft", "probs": {"theft": 0.9}}

class VideoRequest(BaseModel):
    video_url: Optional[str] = None
    upload_path: Optional[str] = None
    rtsp: Optional[str] = None

@router.post("/predict/video")
def predict_video(req: VideoRequest):
    """Enqueue video for async analysis."""
    # TODO: Enqueue job
    return {"job_id": "job123"}
