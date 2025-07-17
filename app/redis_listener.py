import asyncio
import redis
from app.websockets import WebSocketManager

# Shared instance to be imported in FastAPI
ws_manager = WebSocketManager()

async def redis_signal_listener():
    """Listens to Redis signal_channel and broadcasts to WebSocket clients"""
    r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe("signal_channel")

    while True:
        message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message:
            data = message["data"]
            await ws_manager.broadcast(data)
        await asyncio.sleep(0.1)
