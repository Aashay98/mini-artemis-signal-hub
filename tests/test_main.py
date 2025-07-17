import pytest
from fastapi.testclient import TestClient
from app.main import app
from httpx import AsyncClient

client = TestClient(app)

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ticks_post_and_signal(monkeypatch):
    ticks = [{
        "symbol": "AAPL",
        "ts": "2025-07-16T13:30:00Z",
        "open": 100,
        "high": 105,
        "low": 99,
        "close": 104,
        "volume": 123456
    }]
    # Patch Celery async call to run sync for test
    monkeypatch.setattr("app.tasks.process_batch_ticks.delay", lambda x: None)
    response = client.post("/ticks", json=ticks)
    assert response.status_code == 200
    assert response.json()["status"] == "received"
    assert response.json()["count"] == 1


def test_metrics():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text  # Standard Prometheus metric

def test_ticks_empty_list():
    client = TestClient(app)
    response = client.post("/ticks", json=[])
    assert response.status_code == 200
    assert response.json()["count"] == 0
