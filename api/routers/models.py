from fastapi import APIRouter

router = APIRouter()

@router.post("/models/load")
def load_model():
    """Load or refresh the Hugging Face model."""
    # TODO: Implement model loading logic
    return {"status": "model loaded"}
