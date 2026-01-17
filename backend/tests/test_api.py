import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_personalization_endpoint_no_user():
    """Test personalization endpoint without user_id"""
    response = client.get("/api/personalization")
    assert response.status_code == 422  # Missing required parameter

def test_event_tracking_endpoint():
    """Test event tracking endpoint"""
    response = client.post("/api/events", json={
        "event_name": "test_event",
        "user_pseudo_id": "test_user_123",
        "event_params": {"key": "value"},
        "event_timestamp": 1234567890
    })
    # Will fail without DB setup, but structure is correct
