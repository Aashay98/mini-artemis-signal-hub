import pytest
from app.tasks import classify_sma, compute_sma

@pytest.mark.parametrize("sma_20,sma_50,expected", [
    (105, 100, "BUY"),
    (100, 105, "SELL"),
    (100, 100, "HOLD"),
    (None, 100, "HOLD"),
    (100, None, "HOLD"),
])
def test_classify_sma(sma_20, sma_50, expected):
    assert classify_sma(sma_20, sma_50) == expected


def test_compute_sma_not_enough_data(monkeypatch):
    class DummyDB:
        def execute(self, stmt): return type("Dummy", (), {"scalars": lambda self: type("Dummy", (), {"all": lambda self: [type("Dummy", (), {"close": 1.0})() for _ in range(10)]})()})()
    sma_20, sma_50 = compute_sma("AAPL", DummyDB())
    assert sma_20 is None and sma_50 is None

