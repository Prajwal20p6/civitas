import pytest
import os
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agents"))

from src.schemas import IncidentInput
from src.agents.orchestrator import OrchestratorAgent


@pytest.fixture
def demo_scenario():
    data_path = os.path.join("data", "demo_scenario_final.json")
    if not os.path.exists(data_path):
        data_path = os.path.join("agents", "data", "demo_scenario_final.json")
    with open(data_path, "r") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_orchestrator_integration_end_to_end(demo_scenario):
    """Verify that Orchestrator runs all sub-agents sequentially/in parallel end-to-end."""
    orchestrator = OrchestratorAgent()

    # Sanitize location dictionary to contain only numeric lat/lng fields
    raw_location = demo_scenario.get("location") or {"lat": 37.421, "lng": -122.084}
    location = {k: float(v) for k, v in raw_location.items() if k in ["lat", "lng"]}

    incident = IncidentInput(
        incident_type=demo_scenario.get("incident_type", "medical_emergency"),
        description=demo_scenario["description"],
        location=location,
        current_time="17:45",
        base_eta_to_destination=demo_scenario.get("baseline_eta_minutes", 22),
    )

    decision = await orchestrator.execute(incident)

    assert decision.incident_id is not None
    assert decision.winner in ["route_a_speed_first", "route_b_fairness_first"]
    assert decision.requires_approval is True
    assert (
        "Surface Streets" in decision.reasoning_summary
        or "Highway 1" in decision.reasoning_summary
    )
