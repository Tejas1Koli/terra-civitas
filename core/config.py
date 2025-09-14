import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    HF_MODEL: str = os.getenv("HF_MODEL", "Nikeytas/google-vit-best-crime-detector")
    DEVICE: str = os.getenv("DEVICE", "auto")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://user:pass@postgres:5432/sentinel")
    FRAME_FPS: int = int(os.getenv("FRAME_FPS", 2))
    THRESHOLD: float = float(os.getenv("THRESHOLD", 0.7))
    CONSECUTIVE: int = int(os.getenv("CONSECUTIVE", 3))
    STORE_CLIPS: bool = os.getenv("STORE_CLIPS", "false").lower() == "true"
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://minio:9000")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "incidents")

settings = Settings()
