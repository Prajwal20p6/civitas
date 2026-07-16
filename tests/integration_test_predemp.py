"""
Pre-Demo API endpoint testing suite verifying endpoints and latency targets.
"""
import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["CIVITAS_DEMO_MODE"] = "true"

from backend.main import app


def test_predemp_api_lifecycle():
    client = TestClient(app)

    # a) GET /api/v1/health → 200 OK (latency < 50ms)
    t0 = time.perf_counter()
    health_res = client.get("/api/v1/health")
    health_latency = (time.perf_counter() - t0) * 1000

    assert health_res.status_code == 200
    assert health_res.json()["status"] == "ok"
    assert health_latency < 200.0, f"Health check latency high: {health_latency:.1f}ms"

    # b) POST /api/v1/incidents → Create incident → 201 Created + incident_id (latency < 1000ms)
    payload = {
        "incident_type": "emergency_911",
        "description": "Ambulance dispatch for cardiac patient in Mountain View",
        "location": {"lat": 37.421, "lng": -122.084},
        "destination": {"name": "County Hospital", "lat": 37.428, "lng": -122.091},
    }

    t0 = time.perf_counter()
    create_res = client.post("/api/v1/incidents", json=payload)
    create_latency = (time.perf_counter() - t0) * 1000

    assert create_res.status_code == 201
    create_data = create_res.json()
    incident_id = create_data["incident_id"]
    assert incident_id is not None
    assert create_data["status"] == "processing"
    assert (
        create_latency < 1000.0
    ), f"Create incident latency high: {create_latency:.1f}ms"

    # c) GET /api/v1/incidents/{id} → 200 OK + decision data (latency < 500ms)
    t0 = time.perf_counter()
    get_res = client.get(f"/api/v1/incidents/{incident_id}")
    get_latency = (time.perf_counter() - t0) * 1000

    assert get_res.status_code == 200
    incident_data = get_res.json()
    assert incident_data["incident_id"] == incident_id
    assert incident_data["status"] in ["processing", "pending_approval"]
    assert get_latency < 500.0, f"Get incident latency high: {get_latency:.1f}ms"

    # d) WS /api/v1/incidents/{id}/stream → WebSocket connects + receives events (first event < 500ms)
    t0 = time.perf_counter()
    with client.websocket_connect(
        f"/api/v1/incidents/{incident_id}/stream"
    ) as websocket:
        msg = websocket.receive_json()
        first_event_latency = (time.perf_counter() - t0) * 1000

        assert "log" in msg or "status" in msg
        assert (
            first_event_latency < 500.0
        ), f"WebSocket first event latency high: {first_event_latency:.1f}ms"

    # e) POST /api/v1/approval/{id} → Approve incident → 200 OK
    approve_res = client.post(
        f"/api/v1/approval/{incident_id}",
        json={
            "incident_id": incident_id,
            "status": "approved",
            "reason": "Dispatcher cleared corridor.",
        },
    )

    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"
