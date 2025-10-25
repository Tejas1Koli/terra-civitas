
import sys
import os
from ml.video_io import iter_frames
from ml.inference import predict_batch
import cv2

def main():
    video_path = "recordings/webcam_20251025_160647.mp4"  # Change to your video file path
    results = []
    frames = []
    
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        print(f"Current directory: {os.getcwd()}")
        return 1
    
    try:
        # Collect frames for batch prediction
        print(f"Loading video from: {video_path}")
        frame_count = 0
        for frame in iter_frames(video_path, fps_out=2):
            frames.append(frame)
            frame_count += 1
            if frame_count % 10 == 0:
                print(f"Loaded {frame_count} frames...")
        
        print(f"Total frames loaded: {frame_count}")
        
        if not frames:
            print("Error: No frames extracted from video")
            return 1
        
        print(f"Running predictions on {len(frames)} frames...")
        batch_preds = predict_batch(frames)
        
        for idx, preds in enumerate(batch_preds):
            print(f"Frame {idx}: {preds}")
            results.append(preds)
        
        print(f"Successfully processed {len(results)} frames")
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return 1
    except RuntimeError as e:
        print(f"Error: Runtime error - {e}")
        return 1
    except Exception as e:
        print(f"Error: Unexpected error - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())