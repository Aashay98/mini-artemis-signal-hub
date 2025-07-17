import pytest
from app.tasks import classify_sma, compute_sma, process_batch_ticks

def test_classify_sma_all_cases():
    assert classify_sma(11, 10) == "BUY"
    assert classify_sma(9, 10) == "SELL"
    assert classify_sma(10, 10) == "HOLD"
    assert classify_sma(None, 10) == "HOLD"
    assert classify_sma(10, None) == "HOLD"


def test_compute_sma_not_enough_data2(monkeypatch):
    class DummyDB:
        def execute(self, stmt): return type("Dummy", (), {"scalars": lambda self: type("Dummy", (), {"all": lambda self: [type("Dummy", (), {"close": 1.0})() for _ in range(10)]})()})()
    sma_20, sma_50 = compute_sma("AAPL", DummyDB())
    assert sma_20 is None and sma_50 is None

def test_enqueue_ticks_handles_empty(monkeypatch):
    class DummyDB:
        def add_all(self, items): pass
        def commit(self): pass
        def close(self): pass
    monkeypatch.setattr("app.tasks.SessionLocal", lambda: DummyDB())
    class DummyRedis:
        def set(self, *a, **k): pass
        def publish(self, *a, **k): pass
    monkeypatch.setattr("app.tasks.redis_client", DummyRedis())
    process_batch_ticks([])
