from pydantic import BaseModel
from typing import List, Dict, Optional

class FramePrediction(BaseModel):
    label: str
    probs: Dict[str, float]

class Incident(BaseModel):
    id: int
    stream_id: int
    started_at: str
    ended_at: str
    label: str
    confidence: float
    clip_url: Optional[str] = None

class Stream(BaseModel):
    id: int
    name: str
    rtsp_url: str
    active: bool

class JobStatus(BaseModel):
    id: str
    status: str
    result: Optional[Dict] = None
