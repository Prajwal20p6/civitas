import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

# Add workspace root to sys.path so we can import backend.main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

client = TestClient(app)

from unittest.mock import patch


def test_create_incident_latency():
    """Verify that creating an incident responds in <100ms and returns correct schema."""
    payload = {
        "incident_type": "emergency_911",
        "description": "Ambulance dispatch for cardiac patient near Palo Alto",
        "location": {"lat": 37.421, "lng": -122.084},
        "destination": {"name": "County Hospital", "lat": 37.438, "lng": -122.143},
    }

    with patch("backend.main.execute_orchestration_pipeline") as mock_pipeline:
        start_time = time.perf_counter()
        response = client.post("/api/v1/incidents", json=payload)
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        # Assert performance threshold (<100ms)
        assert (
            duration_ms < 100
        ), f"Response latency exceeded 100ms threshold: {duration_ms:.2f}ms"

        # Assert response code and payload structure
        assert response.status_code == 201
        data = response.json()
        assert "incident_id" in data
        assert data["status"] == "processing"
        assert "ADK Orchestrator invoked" in data["message"]


def test_incident_lifecycle_endpoints():
    """Verify incident trace status fetch and human approval updates."""
    # 1. Create incident
    payload = {
        "incident_type": "emergency_911",
        "description": "Ambulance dispatch for stroke patient",
        "location": {"lat": 37.421, "lng": -122.084},
        "destination": {"name": "County Hospital", "lat": 37.438, "lng": -122.143},
    }
    create_res = client.post("/api/v1/incidents", json=payload)
    incident_id = create_res.json()["incident_id"]

    # Give background task a small yield to run orchestrator pipeline
    time.sleep(0.5)

    # 2. Get status trace
    get_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_res.status_code == 200
    incident = get_res.json()
    assert incident["incident_id"] == incident_id
    assert incident["status"] in ["processing", "pending_approval", "executing"]

    # 3. Submit operator approval
    approval_payload = {
        "incident_id": incident_id,
        "status": "approved",
        "reason": "Operator manually validated: corridor green waves approved.",
    }
    approval_res = client.post(f"/api/v1/approval/{incident_id}", json=approval_payload)
    assert approval_res.status_code == 200
    approval_data = approval_res.json()
    assert approval_data["status"] == "approved"

    # 4. Verify updated status
    verify_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert verify_res.json()["status"] == "executing"


def test_zone_forecast_endpoint():
    """Verify that the forecast route returns correct predictive congestion values."""
    response = client.get("/api/v1/forecast/zone_palo_alto_01")
    assert response.status_code == 200
    data = response.json()
    assert data["zone_id"] == "zone_palo_alto_01"
    assert "current_congestion_index" in data
    assert "prediction_30_min" in data
    assert data["trend"] in ["rising", "falling", "stable"]


def test_websocket_reasoning_stream():
    """Verify WebSocket client successfully connects and streams logs."""
    # 1. Create incident
    payload = {
        "incident_type": "emergency_911",
        "description": "Ambulance dispatch for cardiac arrest",
        "location": {"lat": 37.421, "lng": -122.084},
        "destination": {"name": "County Hospital", "lat": 37.438, "lng": -122.143},
    }
    create_res = client.post("/api/v1/incidents", json=payload)
    incident_id = create_res.json()["incident_id"]

    # 2. Connect to WebSocket stream
    with client.websocket_connect(
        f"/api/v1/incidents/{incident_id}/stream"
    ) as websocket:
        # Give backend pipeline time to push logs
        time.sleep(0.5)

        # Receive first streamed log packet
        data = websocket.receive_json()
        assert "log" in data
        assert len(data["log"]) > 0
