"""
Demo end-to-end integration test validating full mock scenario workflow.
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


def test_demo_e2e_full_flow():
    client = TestClient(app)
    t_start = time.perf_counter()

    payload = {
        "incident_type": "emergency_911",
        "description": "Ambulance dispatch for cardiac patient in Los Angeles Downtown Area",
        "location": {"lat": 34.0522, "lng": -118.2437},
        "destination": {"name": "County Hospital", "lat": 34.0722, "lng": -118.2637},
    }

    # 1. Create incident via API
    create_res = client.post("/api/v1/incidents", json=payload)
    assert create_res.status_code == 201
    incident_id = create_res.json()["incident_id"]
    assert incident_id is not None

    # 2. Connect to WebSocket stream and consume reasoning events
    logs_received = []
    with client.websocket_connect(
        f"/api/v1/incidents/{incident_id}/stream"
    ) as websocket:
        # Read the historical logs from the WS stream
        for _ in range(9):
            try:
                msg = websocket.receive_json()
                if "log" in msg:
                    logs_received.append(msg["log"])
            except Exception:
                break

    # Verify reasoning stream gets 6+ events
    assert len(logs_received) >= 6, f"Expected 6+ events, got {len(logs_received)}"

    # 3. Verify simulation scores received (92 vs 74)
    get_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_res.status_code == 200
    incident_data = get_res.json()
    assert incident_data["negotiation_result"]["score_a"] == 92.0
    assert incident_data["negotiation_result"]["score_b"] == 74.0
    assert incident_data["status"] == "pending_approval"

    # 4. Send operator approval
    approve_res = client.post(
        f"/api/v1/approval/{incident_id}",
        json={
            "incident_id": incident_id,
            "status": "approved",
            "reason": "Approved preemption green wave corridor.",
        },
    )
    assert approve_res.status_code == 200

    # 5. Verify execution complete
    verify_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "executing"

    total_latency_sec = time.perf_counter() - t_start
    assert total_latency_sec < 90.0, f"Demo E2E took too long: {total_latency_sec:.1f}s"
