import pytest
from app.websockets import WebSocketManager

class DummyWS:
    def __init__(self):
        self.texts = []
        self.accepted = False
    async def accept(self):
        self.accepted = True
    async def send_text(self, msg):
        self.texts.append(msg)

@pytest.mark.asyncio
async def test_websocket_manager():
    ws = DummyWS()
    mgr = WebSocketManager()
    await mgr.connect(ws)
    assert ws.accepted
    await mgr.broadcast("foo")
    assert ws.texts == ["foo"]
    await mgr.disconnect(ws)
    assert ws not in mgr.active_connections
