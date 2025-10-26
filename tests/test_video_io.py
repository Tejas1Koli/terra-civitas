"""
Unit tests for ml/video_io.py - Video I/O operations
"""

import pytest
import os
import tempfile
import numpy as np
import cv2
from ml.video_io import iter_frames


class TestIterFrames:
    """Test video frame iteration"""
    
    def test_iter_frames_with_valid_video(self, sample_video_path):
        """Test frame iteration with valid video file"""
        frames = list(iter_frames(sample_video_path, fps_out=2))
        
        # Should extract frames
        assert len(frames) > 0
        # Each frame should be numpy array
        assert all(isinstance(f, np.ndarray) for f in frames)
        # Frames should be 3-channel (BGR)
        assert all(f.ndim == 3 and f.shape[2] == 3 for f in frames)
    
    def test_iter_frames_fps_sampling(self, sample_video_path):
        """Test FPS sampling works correctly"""
        # Lower FPS = fewer frames
        frames_2fps = list(iter_frames(sample_video_path, fps_out=2))
        frames_5fps = list(iter_frames(sample_video_path, fps_out=5))
        
        # Should extract fewer frames at lower FPS
        # (fps_out=5 should give more frames than fps_out=2)
        assert len(frames_5fps) >= len(frames_2fps)
    
    def test_iter_frames_nonexistent_file(self):
        """Test iter_frames with non-existent file"""
        with pytest.raises(RuntimeError, match="Video file not found"):
            list(iter_frames("/path/that/does/not/exist.mp4", fps_out=2))
    
    def test_iter_frames_invalid_fps(self, sample_video_path):
        """Test iter_frames with invalid FPS"""
        with pytest.raises(ValueError, match="fps_out must be greater than 0"):
            list(iter_frames(sample_video_path, fps_out=0))
        
        with pytest.raises(ValueError, match="fps_out must be greater than 0"):
            list(iter_frames(sample_video_path, fps_out=-1))
    
    def test_iter_frames_frame_properties(self, sample_video_path):
        """Test that frames have correct properties"""
        frames = list(iter_frames(sample_video_path, fps_out=10))
        
        if len(frames) > 0:
            frame = frames[0]
            
            # Frame should be uint8
            assert frame.dtype == np.uint8
            
            # Frame shape should be (height, width, 3)
            assert len(frame.shape) == 3
            assert frame.shape[2] == 3
            
            # Values should be in valid range
            assert frame.min() >= 0
            assert frame.max() <= 255
    
    def test_iter_frames_respects_fps_out_1(self, sample_video_path):
        """Test iter_frames with fps_out=1"""
        frames = list(iter_frames(sample_video_path, fps_out=1))
        
        # With fps_out=1, should get approximately 1 frame per second of video
        # For 30 frame video at 30fps = 1 second video
        # At 1 fps output should get ~1 frame
        assert len(frames) >= 1
    
    def test_iter_frames_different_fps_ratios(self, sample_video_path):
        """Test frame iteration with different FPS ratios"""
        fps_1 = list(iter_frames(sample_video_path, fps_out=1))
        fps_5 = list(iter_frames(sample_video_path, fps_out=5))
        fps_10 = list(iter_frames(sample_video_path, fps_out=10))
        
        # Higher fps_out should give more frames
        assert len(fps_1) <= len(fps_5)
        assert len(fps_5) <= len(fps_10)
    
    def test_iter_frames_returns_generator(self, sample_video_path):
        """Test that iter_frames returns a generator/iterator"""
        result = iter_frames(sample_video_path, fps_out=2)
        
        # Should be iterable
        assert hasattr(result, '__iter__')
    
    def test_iter_frames_memory_efficiency(self, sample_video_path):
        """Test that iter_frames is memory efficient (uses generator)"""
        import sys
        
        # Get iterator but don't consume it all
        frame_iter = iter_frames(sample_video_path, fps_out=2)
        
        # Get first frame
        first_frame = next(frame_iter)
        assert isinstance(first_frame, np.ndarray)
        
        # Iterator should still be usable
        try:
            second_frame = next(frame_iter)
            assert isinstance(second_frame, np.ndarray)
        except StopIteration:
            # Video might only have one frame
            pass


class TestIterFramesEdgeCases:
    """Test edge cases for video iteration"""
    
    def test_iter_frames_empty_result(self):
        """Test behavior with video that yields no frames (edge case)"""
        # Create minimal video
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            temp_video = f.name
        
        try:
            # Create minimal video with 1 frame
            fourcc = int(cv2.VideoWriter.fourcc('m', 'p', '4', 'v'))
            out = cv2.VideoWriter(temp_video, fourcc, 30.0, (640, 480))
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
            out.release()
            
            # Try to read
            frames = list(iter_frames(temp_video, fps_out=30))
            # Should have at least the first frame
            assert len(frames) >= 1
        
        finally:
            if os.path.exists(temp_video):
                os.remove(temp_video)
    
    def test_iter_frames_high_fps_output(self, sample_video_path):
        """Test iter_frames with very high fps_out"""
        frames = list(iter_frames(sample_video_path, fps_out=60))
        
        # Even with high fps_out, should not crash
        assert isinstance(frames, list)
    
    def test_iter_frames_large_fps_ratio(self, sample_video_path):
        """Test iter_frames when fps_out > original fps"""
        # Request more frames than available
        frames = list(iter_frames(sample_video_path, fps_out=1000))
        
        # Should still work, just fewer frames
        assert isinstance(frames, list)


class TestVideoCapture:
    """Test video capture wrapper integration"""
    
    def test_iter_frames_with_different_video_sizes(self):
        """Test iter_frames handles different video sizes"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            temp_video = f.name
        
        try:
            # Create video with specific size
            size = (320, 240)
            fourcc = int(cv2.VideoWriter.fourcc('m', 'p', '4', 'v'))
            out = cv2.VideoWriter(temp_video, fourcc, 30.0, size)
            
            # Write frames
            for i in range(10):
                frame = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
                out.write(frame)
            out.release()
            
            # Read frames
            frames = list(iter_frames(temp_video, fps_out=2))
            
            # Check frame sizes
            for frame in frames:
                assert frame.shape == (240, 320, 3)
        
        finally:
            if os.path.exists(temp_video):
                os.remove(temp_video)
    
    def test_iter_frames_with_corrupted_file(self):
        """Test iter_frames with corrupted/invalid video file"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            temp_video = f.name
            # Write garbage data
            f.write(b"This is not a valid video file")
        
        try:
            # Should raise error when trying to open
            with pytest.raises(RuntimeError, match="Failed to open"):
                list(iter_frames(temp_video, fps_out=2))
        
        finally:
            if os.path.exists(temp_video):
                os.remove(temp_video)
