# Sentinel-Crime

Detect crime in video streams using the Hugging Face ViT model (`Nikeytas/google-vit-best-crime-detector`).

## Quickstart

```sh
docker compose up --build
```

## Configuring Model & Thresholds
- Edit `.env` or set environment variables.
- Key variables: `HF_MODEL`, `DEVICE`, `THRESHOLD`, `FRAME_FPS`, `CONSECUTIVE`, `STORE_CLIPS`.

## API Reference

### Health
```sh
curl -s http://localhost:8000/health
```

### Load model
```sh
curl -X POST http://localhost:8000/models/load
```

### Predict a frame (local file)
```sh
curl -X POST "http://localhost:8000/predict/frame" \
  -F "file=@tests/assets/frame.jpg"
```

### Predict a video (URL)
```sh
curl -X POST "http://localhost:8000/predict/video" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://example.com/clip.mp4"}'
```

### Job status
```sh
curl -s http://localhost:8000/jobs/<job_id>
```

### Register an RTSP stream
```sh
curl -X POST "http://localhost:8000/streams/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Cam-1","rtsp_url":"rtsp://user:pass@ip:554/stream1","fps":2,"active":false}'
```

## Streaming Guide
- Register a stream via `/streams/register`.
- Start/stop streams with `/streams/{id}/start` and `/streams/{id}/stop`.
- Watch alerts via `/alerts/ws` (WebSocket).

## Performance Tips
- Tune `FRAME_FPS`, `THRESHOLD`, `CONSECUTIVE`, and batch size in `.env`.
- Use GPU for higher throughput.

## Limitations & FAQ
- Model is trained on UCF-Crime; expect domain shift.
- Frame-based model; temporal context is approximated.
- Not edge-optimized; see docs for tips.
- All alerts are suggestions; human review required.

## License
MIT
