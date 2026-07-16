"""
Full end-to-end integration test for the CIVITAS pipeline.

Uses a deterministic mock pipeline (pre-computed demo data) to avoid
real LLM/Gemini API calls, ensuring tests are fast, offline-safe, and
complete in <2 seconds in demo mode.
"""
import os
import sys
import json
import time
import pytest

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load pre-computed demo scenario for deterministic assertions
_scenario_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "demo_scenario_final.json"
)
with open(_scenario_path, "r") as f:
    _demo_scenario = json.load(f)

# Set demo mode environment variable
os.environ["CIVITAS_DEMO_MODE"] = "true"

from fastapi.testclient import TestClient
from backend.main import app


def test_full_integration_e2e_flow():
    """
    Full E2E integration test with deterministic mock pipeline (no LLM calls):
    1. Create incident via POST /api/v1/incidents
    2. Connect to WebSocket stream and consume agent reasoning updates
    3. Verify all 6 agents execute (via log messages)
    4. Verify Firestore state is populated with decision metrics
    5. Post manual operator approval
    6. Verify final execution state transition
    """
    client = TestClient(app)

    payload = {
        "incident_type": _demo_scenario["incident_type"],
        "description": _demo_scenario["description"],
        "location": {
            "lat": _demo_scenario["location"]["lat"],
            "lng": _demo_scenario["location"]["lng"],
        },
        "destination": {
            "name": _demo_scenario["destination"]["name"],
            "lat": _demo_scenario["destination"]["lat"],
            "lng": _demo_scenario["destination"]["lng"],
        },
    }

    # ── Step 1: Create Incident ──
    start_time = time.perf_counter()
    create_res = client.post("/api/v1/incidents", json=payload)
    total_duration_ms = (time.perf_counter() - start_time) * 1000

    assert (
        create_res.status_code == 201
    ), f"Expected 201, got {create_res.status_code}: {create_res.text}"
    create_data = create_res.json()
    incident_id = create_data["incident_id"]
    assert incident_id is not None
    assert create_data["status"] == "processing"

    # In demo mode with mock pipeline, entire request should finish in <10s
    assert (
        total_duration_ms < 10_000
    ), f"E2E pipeline exceeded 10s: {total_duration_ms:.0f}ms"

    # ── Step 2: Connect to WebSocket & verify reasoning logs ──
    logs_received = []
    with client.websocket_connect(
        f"/api/v1/incidents/{incident_id}/stream"
    ) as websocket:
        # Since BackgroundTasks run synchronously in FastAPI TestClient, all logs are
        # already processed and written. They will be sent immediately as history.
        # We read the 9 expected log entries (8 progressive + 1 final pipeline log).
        for _ in range(9):
            try:
                msg = websocket.receive_json()
                if "log" in msg:
                    logs_received.append(msg["log"])
            except Exception:
                break

    # ── Step 3: Verify all 6 agents executed (via log content) ──
    joined = "\n".join(logs_received)
    assert "Perception Agent" in joined, f"Missing Perception Agent logs. Got: {joined}"
    assert "Route Agent A" in joined, f"Missing Route Agent A logs. Got: {joined}"
    assert "Route Agent B" in joined, f"Missing Route Agent B logs. Got: {joined}"
    assert "Simulation Agent" in joined, f"Missing Simulation Agent logs. Got: {joined}"
    assert (
        "Explainability Agent" in joined
    ), f"Missing Explainability Agent logs. Got: {joined}"
    assert "Orchestrator" in joined, f"Missing Orchestrator logs. Got: {joined}"

    # ── Step 4: Verify Firestore state populated ──
    get_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_res.status_code == 200
    state = get_res.json()

    assert state["incident_id"] == incident_id
    assert state["status"] == "pending_approval"
    assert state["perception"] is not None
    assert state["route_a_proposal"] is not None
    assert state["route_b_proposal"] is not None
    assert state["negotiation_result"] is not None
    assert state["explainability"] is not None

    # Verify pre-computed scoring values
    assert state["negotiation_result"]["score_a"] == 92.0
    assert state["negotiation_result"]["score_b"] == 74.0
    assert state["negotiation_result"]["winner"] == "route_a_speed_first"

    # ── Step 5: Simulate operator approval ──
    approve_res = client.post(
        f"/api/v1/approval/{incident_id}",
        json={
            "incident_id": incident_id,
            "status": "approved",
            "reason": "Operator clears green wave preemption corridor.",
        },
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"

    # ── Step 6: Verify final execution state ──
    verify_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "executing"
