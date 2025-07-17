import asyncio
from http.client import HTTPException
from typing import List
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import redis
from app.redis_listener import redis_signal_listener
from app.tasks import process_batch_ticks
from app.websockets import WebSocketManager

app = FastAPI()

class Tick(BaseModel):
    symbol: str
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
ws_manager = WebSocketManager()

@app.on_event("startup")
async def startup_event():
    # Start Redis listener in background
    loop = asyncio.get_event_loop()
    loop.create_task(redis_signal_listener())

@app.post("/ticks")
def ingest_ticks(ticks: List[Tick]):
    """Accept batch of ticks and enqueue processing task."""
    try:
        print(ticks)
        process_batch_ticks.delay([tick.dict() for tick in ticks])
        return {"status": "received", "count": len(ticks)}
    except Exception as e:
        raise HTTPException(500,str(e))

@app.websocket("/ws/signals")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection for signal updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() 
    except Exception:
        await ws_manager.disconnect(websocket)

@app.get("/healthz")
async def health_check():
    """Healthcheck endpoint."""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return {"metrics": "To be configured with Prometheus integration"}