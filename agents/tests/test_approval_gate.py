import pytest
import asyncio
from unittest.mock import MagicMock, patch
from src.schemas import ApprovalGateInput
from src.agents.approval_gate import ApprovalGateAgent


@pytest.fixture
def mock_db():
    db = MagicMock()
    return db


@pytest.fixture
def sample_gate_input():
    return ApprovalGateInput(
        incident_id="test_incident_123",
        decision="route_a_speed_first",
        reasoning="Test reasoning summary",
        impact_score=0.85,
        timestamp="2026-07-16T12:00:00Z",
    )


@pytest.mark.asyncio
async def test_auto_approval_low_impact(mock_db, sample_gate_input):
    """Verify that low-impact incidents are automatically approved without operator intervention."""
    sample_gate_input.impact_score = 0.35  # Below AUTO_APPROVE_THRESHOLD = 0.5

    agent = ApprovalGateAgent(db_client=mock_db)
    result = await agent.execute(sample_gate_input)

    assert result["status"] == "auto_approved"
    assert "below auto-approval threshold" in result["reason"]
    assert result["wait_time_seconds"] == 0.0

    # Verify DB updates
    mock_db.update_incident.assert_called_once_with(
        "test_incident_123", {"status": "executing"}
    )
    mock_db.push_reasoning_log.assert_called_once()


@pytest.mark.asyncio
async def test_demo_mode_auto_approval(mock_db, sample_gate_input):
    """Verify that demo mode auto-approves after the designated delay."""
    agent = ApprovalGateAgent(db_client=mock_db)

    with patch.dict("os.environ", {"CIVITAS_DEMO_MODE": "true"}), patch(
        "src.agents.approval_gate.DEMO_AUTO_APPROVE_DELAY", 0.01
    ), patch("asyncio.sleep", return_value=None) as mock_sleep:
        result = await agent.execute(sample_gate_input)

        assert result["status"] == "approved"
        assert "Demo mode auto-approval" in result["reason"]
        mock_sleep.assert_called_once_with(0.01)

        # Verify DB updates
        mock_db.update_incident.assert_any_call(
            "test_incident_123", {"status": "pending_approval"}
        )
        mock_db.update_incident.assert_any_call(
            "test_incident_123", {"status": "executing"}
        )


@pytest.mark.asyncio
async def test_live_operator_approved(mock_db, sample_gate_input):
    """Verify that the agent waits and successfully resolves when approved by an operator."""
    agent = ApprovalGateAgent(db_client=mock_db)

    # Configure mock DB to simulate operator input after one polling loop
    mock_db.get_incident.side_effect = [
        {"status": "pending_approval"},
        {
            "status": "executing",
            "operator_decision": {
                "status": "approved",
                "reason": "Clearance approved by Dispatcher",
            },
        },
    ]

    with patch.dict("os.environ", {"CIVITAS_DEMO_MODE": "false"}), patch(
        "src.agents.approval_gate.POLL_INTERVAL_SECONDS", 0.01
    ), patch("asyncio.sleep", return_value=None):
        result = await agent.execute(sample_gate_input)

        assert result["status"] == "approved"
        assert result["reason"] == "Clearance approved by Dispatcher"

        # Verify DB updates
        mock_db.update_incident.assert_called_once_with(
            "test_incident_123", {"status": "pending_approval"}
        )
        assert mock_db.get_incident.call_count == 2


@pytest.mark.asyncio
async def test_live_operator_denied(mock_db, sample_gate_input):
    """Verify that the agent waits and successfully resolves when denied by an operator."""
    agent = ApprovalGateAgent(db_client=mock_db)

    mock_db.get_incident.side_effect = [
        {"status": "pending_approval"},
        {
            "status": "denied",
            "operator_decision": {
                "status": "denied",
                "reason": "Dispatcher override: alternative route selected",
            },
        },
    ]

    with patch.dict("os.environ", {"CIVITAS_DEMO_MODE": "false"}), patch(
        "src.agents.approval_gate.POLL_INTERVAL_SECONDS", 0.01
    ), patch("asyncio.sleep", return_value=None):
        result = await agent.execute(sample_gate_input)

        assert result["status"] == "denied"
        assert result["reason"] == "Dispatcher override: alternative route selected"


@pytest.mark.asyncio
async def test_live_operator_timeout(mock_db, sample_gate_input):
    """Verify that the agent times out when no operator decision is received within the limit."""
    agent = ApprovalGateAgent(db_client=mock_db)

    # DB always returns pending_approval
    mock_db.get_incident.return_value = {"status": "pending_approval"}

    with patch.dict("os.environ", {"CIVITAS_DEMO_MODE": "false"}), patch(
        "src.agents.approval_gate.POLL_INTERVAL_SECONDS", 0.01
    ), patch("src.agents.approval_gate.APPROVAL_TIMEOUT_SECONDS", 0.02), patch(
        "asyncio.sleep", return_value=None
    ):
        result = await agent.execute(sample_gate_input)

        assert result["status"] == "timeout"
        assert "No operator response" in result["reason"]

        # Verify timeout status was written
        mock_db.update_incident.assert_any_call(
            "test_incident_123", {"status": "timeout"}
        )
