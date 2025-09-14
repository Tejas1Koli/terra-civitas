from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class StreamRegister(BaseModel):
    name: str
    rtsp_url: str
    fps: int
    active: bool = False

@router.post("/streams/register")
def register_stream(req: StreamRegister):
    # TODO: Register stream
    return {"stream_id": 1}

@router.post("/streams/{id}/start")
def start_stream(id: int):
    # TODO: Start stream
    return {"status": "started"}

@router.post("/streams/{id}/stop")
def stop_stream(id: int):
    # TODO: Stop stream
    return {"status": "stopped"}

@router.get("/streams/{id}/status")
def stream_status(id: int):
    # TODO: Return stream status
    return {"fps": 2, "last_frame_time": None, "last_alert": None, "errors": []}
