import cv2
from typing import Iterator, Optional

def iter_frames(source: str, fps_out: int = 2) -> Iterator:
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video source: {source}")
    orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_interval = int(round(orig_fps / fps_out))
    count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if count % frame_interval == 0:
                yield frame
            count += 1
    finally:
        cap.release()
