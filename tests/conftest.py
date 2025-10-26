"""
Pytest conftest.py - Shared fixtures and configuration for all tests
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_frame():
    """Create a sample video frame (numpy array)"""
    import numpy as np
    # Create a random BGR frame (480x640x3)
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return frame


@pytest.fixture
def sample_frames(sample_frame):
    """Create multiple sample frames"""
    import numpy as np
    frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(5)]
    return frames


@pytest.fixture
def sample_video_path(tmp_path):
    """Create a temporary video file for testing"""
    import cv2
    import numpy as np
    
    video_path = tmp_path / "test_video.mp4"
    # Use MJPEG codec which is more compatible
    fourcc = int(cv2.VideoWriter.fourcc('m', 'p', '4', 'v'))
    out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
    
    # Write 30 frames
    for i in range(30):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out.write(frame)
    
    out.release()
    return str(video_path)
