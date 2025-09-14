from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.get("/alerts/ws")
async def alerts_ws(websocket: WebSocket):
    # TODO: Implement WebSocket for alerts
    await websocket.accept()
    await websocket.send_json({"alert": "test"})
    await websocket.close()
