import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add root folder and agents folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
)

from backend.firebase_client import FirebaseClient, retry_db_operation
from src.agents.orchestrator import OrchestratorAgent
from src.schemas import IncidentInput


def test_firebase_client_retry_logic():
    """Verify that the database retry mechanism works correctly and raises exception after limit."""
    call_count = 0

    def failing_op():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Intermittent timeout")

    with pytest.raises(ConnectionError):
        retry_db_operation(failing_op, max_retries=3, delay=0.01)

    assert call_count == 3


def test_firebase_client_offline_operations():
    """Verify Firestore and RTDB wrapper CRUD operations in offline mode."""
    client = FirebaseClient()
    assert client.offline_mode is True

    incident_id = "test_inc_123"
    incident_data = {
        "incident_id": incident_id,
        "incident_type": "accident",
        "description": "Fender bender",
        "status": "processing",
    }

    # 1. Create Write
    client.create_incident(incident_id, incident_data)

    # 2. Read Get
    fetched = client.get_incident(incident_id)
    assert fetched is not None
    assert fetched["description"] == "Fender bender"

    # 3. Update Write
    client.update_incident(
        incident_id, {"status": "pending_approval", "extra_field": "val"}
    )
    updated = client.get_incident(incident_id)
    assert updated["status"] == "pending_approval"
    assert updated["extra_field"] == "val"

    # 4. Stream Write and Read
    client.push_reasoning_log(incident_id, "Route Agent proposal A generated.")
    client.push_reasoning_log(incident_id, "Route Agent proposal B generated.")

    logs = client.get_reasoning_logs(incident_id)
    assert len(logs) == 2
    assert logs[0]["message"] == "Route Agent proposal A generated."
    assert logs[1]["message"] == "Route Agent proposal B generated."


@pytest.mark.asyncio
async def test_orchestrator_wiring_to_firebase():
    """Verify that Orchestrator agent execution actively writes to the FirebaseClient wrapper."""
    client = FirebaseClient()

    # Patch the class reference in the orchestrator's module namespace
    with patch("src.agents.orchestrator.FirebaseClient", return_value=client):
        orchestrator = OrchestratorAgent()

        incident_id = "agent_test_999"
        incident_input = IncidentInput(
            incident_type="emergency_911",
            description="Cardiac dispatch requested.",
            location={"lat": 37.421, "lng": -122.084},
            current_time="17:45",
            base_eta_to_destination=22,
        )

        # Pre-create the incident in mock DB to mirror production lifecycles
        client.create_incident(incident_id, {"incident_id": incident_id})

        # Ingest and execute incident pipeline
        decision = await orchestrator.execute(incident_input, incident_id=incident_id)

        # Verify Orchestrator decision schema is generated
        assert decision.incident_id == incident_id

        # Verify database writes occurred during orchestrator execution
        incident = client.get_incident(incident_id)
        assert incident is not None
        assert incident["perception"] is not None
        assert incident["route_a_proposal"] is not None
        assert incident["route_b_proposal"] is not None
        assert incident["negotiation_result"] is not None
        assert incident["explainability"] is not None

        # Verify that multiple logging updates were sent to database stream
        logs = client.get_reasoning_logs(incident_id)
        assert len(logs) > 0

        # Check first and last log messages
        log_messages = [log["message"] for log in logs]
        assert any("Running Perception Agent" in msg for msg in log_messages)
        assert any("operator Brief:" in msg for msg in log_messages)
