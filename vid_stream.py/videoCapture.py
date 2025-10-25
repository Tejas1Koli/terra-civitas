import cv2
import os
from datetime import datetime
import time
import json

def record_webcam_chunks_json(save_dir="recordings", json_file="videos.json",
                              total_duration=3600, chunk_duration=5, target_size=(224,224)):
    """
    Record webcam for total_duration and save separate videos every chunk_duration seconds.
    Stops when you press 'q' in the OpenCV window.
    Metadata (path, timestamp) is appended to an existing JSON file.
    """
    os.makedirs(save_dir, exist_ok=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return []

    width, height = target_size
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Load existing JSON if it exists
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                video_metadata = json.load(f)
            except json.JSONDecodeError:
                video_metadata = []
    else:
        video_metadata = []

    start_time = time.time()
    print("Recording started. Focus the OpenCV window and press 'q' to stop anytime.")

    while (time.time() - start_time) < total_duration:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(save_dir, f"webcam_{file_timestamp}.mp4")
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (width, height))
        chunk_start = time.time()

        while (time.time() - chunk_start) < chunk_duration:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame_resized = cv2.resize(frame, (width, height))
            out.write(frame_resized)

            cv2.imshow("Recording", frame_resized)

            # Stop if 'q' pressed (window must be focused)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                print("Recording stopped by user")
                out.release()
                cap.release()
                cv2.destroyAllWindows()
                # Save JSON before exiting
                with open(json_file, 'w') as f:
                    json.dump(video_metadata, f, indent=4)
                return video_metadata

        out.release()
        print(f"Saved video chunk: {video_path}")
        # Append metadata
        video_metadata.append({
            "path": video_path,
            "timestamp": timestamp
        })

        # Update JSON after each chunk
        with open(json_file, 'w') as f:
            json.dump(video_metadata, f, indent=4)

    cap.release()
    cv2.destroyAllWindows()
    print(f"All video metadata saved to {os.path.basename(json_file)}")
    return video_metadata

# Example usage
video_metadata = record_webcam_chunks_json(total_duration=3600, chunk_duration=5, target_size=(224,224))
#print("All video metadata:", video_metadata)

