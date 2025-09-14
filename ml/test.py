from ml.video_io import iter_frames
from ml.inference import predict_frame

video_path = "test.mp4"  # Change to your video file path
results = []

for frame in iter_frames(video_path, fps_out=2):  # 2 FPS sampling
    preds = predict_frame(frame)
    print(preds)
    results.append(preds)