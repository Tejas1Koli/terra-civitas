import cv2
from typing import Iterator, Optional
import os

def iter_frames(source: str, fps_out: int = 2) -> Iterator:
    """
    Iterate through video frames at specified output FPS.
    
    Args:
        source: Path to video file
        fps_out: Output frames per second (default: 2)
    
    Yields:
        Frame as numpy array (BGR format from OpenCV)
    
    Raises:
        RuntimeError: If video cannot be opened or if fps_out is invalid
    """
    if not os.path.exists(source):
        raise RuntimeError(f"Video file not found: {source}")
    
    if fps_out <= 0:
        raise ValueError("fps_out must be greater than 0")
    
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video source: {source}")
    
    try:
        orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30
        if orig_fps <= 0:
            orig_fps = 30  # Default fallback
        
        frame_interval = int(round(orig_fps / fps_out))
        count = 0
        frame_yielded = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if count % frame_interval == 0:
                yield frame
                frame_yielded += 1
            count += 1
    finally:
        cap.release()

