# tests/test_redis_listener.py
import pytest
import asyncio

def test_ws_manager_import():
    from app.redis_listener import ws_manager
    assert ws_manager is not None

@pytest.mark.asyncio
async def test_redis_signal_listener_handles_message(monkeypatch):
    from app.redis_listener import redis_signal_listener, ws_manager

    # Mock Redis pubsub to yield a message once, then always None
    class DummyPubSub:
        def __init__(self):
            self.calls = 0
        def subscribe(self, channel):
            pass
        def get_message(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return {"data": "test-signal"}
            return None
    class DummyRedis:
        def pubsub(self):
            return DummyPubSub()
    monkeypatch.setattr("redis.Redis", lambda **kwargs: DummyRedis())

    # Patch broadcast to record messages
    msgs = []
    async def fake_broadcast(message):
        msgs.append(message)
    ws_manager.broadcast = fake_broadcast

    # Run the listener for a couple iterations, then cancel
    task = asyncio.create_task(redis_signal_listener())
    await asyncio.sleep(0.3)
    task.cancel()
    assert "test-signal" in msgs
