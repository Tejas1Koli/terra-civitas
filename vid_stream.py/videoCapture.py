import os
import sys

# set before importing cv2 so native ffmpeg/opencv honors it
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")

import contextlib

@contextlib.contextmanager
def _suppress_stderr_fd():
    """
    Temporarily redirect native stderr (FD 2) to os.devnull to hide FFmpeg/MJPEG lines.
    Works on Windows and Unix; best-effort.
    """
    devnull = None
    old_fd = None
    try:
        devnull = open(os.devnull, "w")
        # duplicate stderr fd
        old_fd = os.dup(2)
        # redirect fd 2 -> devnull
        os.dup2(devnull.fileno(), 2)
        yield
    except Exception:
        yield
    finally:
        try:
            if old_fd is not None:
                os.dup2(old_fd, 2)
                os.close(old_fd)
        except Exception:
            pass
        try:
            if devnull is not None:
                devnull.close()
        except Exception:
            pass

# Temporarily redirect stderr to suppress native FFmpeg/MJPEG logs during cv2 import.
_devnull = None
_old_stderr_fd = None
try:
    _devnull = open(os.devnull, "w")
    if hasattr(sys.stderr, "fileno"):
        _old_stderr_fd = os.dup(sys.stderr.fileno())
        os.dup2(_devnull.fileno(), sys.stderr.fileno())
except Exception:
    _devnull = None
    _old_stderr_fd = None

import cv2

# restore stderr
try:
    if _old_stderr_fd is not None and hasattr(sys.stderr, "fileno"):
        os.dup2(_old_stderr_fd, sys.stderr.fileno())
        os.close(_old_stderr_fd)
    if _devnull is not None:
        _devnull.close()
except Exception:
    pass

# suppress OpenCV/FFmpeg log output (best-effort)
try:
    cv2.setLogLevel(cv2.LOG_LEVEL_ERROR)
except Exception:
    try:
        cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
    except Exception:
        pass

from datetime import datetime
import time
import json
import numpy as np
from urllib.parse import urlparse

def _label_for_source(src, idx):
    if isinstance(src, int):
        return f"camera_{src}"
    try:
        p = urlparse(str(src))
        if p.hostname:
            return p.hostname.replace(":", "_")
    except:
        pass
    # fallback
    return f"source_{idx}"

def record_multi_source_chunks_json(
        save_dir="recordings",
        json_file="videos.json",
        total_duration=3600,
        chunk_duration=5,
        target_size=(224,224),
        phone1_url="http://172.30.58.20:8080/video",
        phone2_url="http://172.30.58.210:8080/video"
    ):

    os.makedirs(save_dir, exist_ok=True)

    sources = [
        0,
        phone1_url,
        phone2_url
    ]

    caps = []
    src_labels = []

    for i, src in enumerate(sources):
        cap = None
        opened = False

        # Local webcam (integer) — prefer Windows camera backends
        if isinstance(src, int):
            for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_VFW, cv2.CAP_ANY):
                try:
                    cap = cv2.VideoCapture(src, backend)
                except Exception:
                    cap = cv2.VideoCapture(src)
                if cap is not None and cap.isOpened():
                    print(f"Opened webcam index {src} with backend {backend}")
                    opened = True
                    break
                else:
                    try:
                        cap.release()
                    except Exception:
                        pass

        # Network/phone streams — try FFMPEG then default
        else:
            for backend in (cv2.CAP_FFMPEG, cv2.CAP_ANY):
                try:
                    cap = cv2.VideoCapture(src, backend)
                except Exception:
                    cap = cv2.VideoCapture(src)
                if cap is not None and cap.isOpened():
                    print(f"Opened stream {src}")
                    opened = True
                    break
                else:
                    try:
                        cap.release()
                    except Exception:
                        pass

        if not opened:
            print(f"Warning: Could not open source: {src} (skipping). Ensure camera not used by other apps and index is correct.")
            continue

        # reduce buffering where supported
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        caps.append(cap)
        src_labels.append(_label_for_source(src, i))

    if not caps:
        print("Error: No video sources available.")
        return

    width, height = target_size
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 20.0

    if os.path.exists(json_file):
        try:
            video_metadata = json.load(open(json_file, 'r'))
        except:
            video_metadata = []
    else:
        video_metadata = []

    start_time = time.time()
    print("Recording started. Press 'q' in any OpenCV window to stop.")

    stop = False
    try:
        while (time.time() - start_time) < total_duration and not stop:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            writers = []
            paths = []
            # create per-source folder and writer
            for label in src_labels:
                src_dir = os.path.join(save_dir, label)
                os.makedirs(src_dir, exist_ok=True)
                video_path = os.path.join(src_dir, f"{label}_{file_timestamp}.mp4")
                out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
                writers.append(out)
                paths.append(video_path)

            chunk_start = time.time()

            while (time.time() - chunk_start) < chunk_duration and not stop:
                frames = []
                for cap_idx, cap in enumerate(caps):
                    # suppress FFmpeg native stderr during read (hides "[mjpeg ...] overread" messages)
                    with _suppress_stderr_fd():
                        ret, frame = cap.read()

                    if not ret or frame is None:
                        # try a quick reconnect if stream fails
                        src = sources[cap_idx]
                        print(f"Warning: read failed for {src_labels[cap_idx]}, attempting reconnect...")
                        try:
                            # suppress FFmpeg stderr during reconnect/open as well
                            cap.release()
                            time.sleep(0.5)
                            with _suppress_stderr_fd():
                                try:
                                    new_cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
                                except Exception:
                                    new_cap = cv2.VideoCapture(src)
                            try:
                                new_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            except Exception:
                                pass
                            caps[cap_idx] = new_cap
                            with _suppress_stderr_fd():
                                ret, frame = new_cap.read()
                        except Exception:
                            ret = False

                    if not ret or frame is None:
                        # black placeholder on persistent failure
                        frame = np.zeros((height, width, 3), dtype=np.uint8)
                    else:
                        frame = cv2.resize(frame, (width, height))
                    writers[cap_idx].write(frame)
                    cv2.imshow(f"Source {src_labels[cap_idx]}", frame)
                    frames.append(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    stop = True
                    break

            # release writers for this chunk
            for w in writers:
                w.release()

            # append metadata per source
            for label, path in zip(src_labels, paths):
                video_metadata.append({
                    "timestamp": timestamp,
                    "source": label,
                    "path": path
                })

            with open(json_file, "w") as f:
                json.dump(video_metadata, f, indent=4)

    finally:
        for cap in caps:
            cap.release()
        cv2.destroyAllWindows()
        print("Recording stopped. Files saved in:", save_dir)

if __name__ == "__main__":
    record_multi_source_chunks_json()
