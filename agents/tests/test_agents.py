import pytest
import os
import json
from src.schemas import (
    IncidentInput,
    RouteAgentInput,
    SimulationInput,
    ExplainabilityInput,
)
from src.agents.perception import PerceptionAgent
from src.agents.route_agents.speed_first import RouteAgentA
from src.agents.route_agents.fairness_first import RouteAgentB
from src.agents.simulation import SimulationAgent
from src.agents.explainability import ExplainabilityAgent
from src.agents.orchestrator import OrchestratorAgent


@pytest.fixture
def sample_incident():
    return IncidentInput(
        incident_type="emergency_911",
        description="Ambulance dispatch for cardiac patient near 5th Ave",
        location={"lat": 37.4219, "lng": -122.0840},
        current_time="2026-07-15T09:30:00Z",
        base_eta_to_destination=22,
    )


@pytest.fixture
def test_scenarios():
    scenarios_path = os.path.join("tests", "fixtures", "test_scenarios.json")
    if not os.path.exists(scenarios_path):
        scenarios_path = os.path.join(
            "agents", "tests", "fixtures", "test_scenarios.json"
        )
    with open(scenarios_path, "r") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_perception_agent(sample_incident):
    agent = PerceptionAgent()
    classification = await agent.execute(sample_incident)
    assert classification.incident_type == "medical_emergency"
    assert classification.severity == "critical"
    assert classification.priority_score == 0.95


@pytest.mark.asyncio
async def test_route_agents():
    input_data = RouteAgentInput(
        incident_location={"lat": 37.4219, "lng": -122.0840},
        destination={"lat": 37.4280, "lng": -122.0910},
        current_traffic_conditions={
            "Surface Streets": "heavy",
            "Highway 1": "moderate",
        },
        objectives={"priority": "optimize_eta"},
    )

    agent_a = RouteAgentA()
    proposal_a = await agent_a.execute(input_data)
    assert proposal_a.agent_id == "route_a_speed_first"
    assert proposal_a.recommended_route == "Surface Streets"
    assert proposal_a.ambulance_eta == 8

    agent_b = RouteAgentB()
    proposal_b = await agent_b.execute(input_data)
    assert proposal_b.agent_id == "route_b_fairness_first"
    assert proposal_b.recommended_route == "Highway 1"
    assert proposal_b.ambulance_eta == 11


@pytest.mark.asyncio
async def test_simulation_agent(sample_incident):
    agent = SimulationAgent()

    input_data = RouteAgentInput(
        incident_location={"lat": 37.4219, "lng": -122.0840},
        destination={"lat": 37.4280, "lng": -122.0910},
        current_traffic_conditions={
            "Surface Streets": "heavy",
            "Highway 1": "moderate",
        },
        objectives={"priority": "optimize_eta"},
    )

    prop_a = await RouteAgentA().execute(input_data)
    prop_b = await RouteAgentB().execute(input_data)
    classification = await PerceptionAgent().execute(sample_incident)

    sim_input = SimulationInput(
        proposal_a=prop_a, proposal_b=prop_b, incident=classification
    )

    res = await agent.execute(sim_input)
    assert res.winner == "route_a_speed_first"
    assert res.score_a > res.score_b
    assert res.counterfactual["time_saved"] == 14


@pytest.mark.asyncio
async def test_explainability_agent(sample_incident):
    input_data = RouteAgentInput(
        incident_location={"lat": 37.4219, "lng": -122.0840},
        destination={"lat": 37.4280, "lng": -122.0910},
        current_traffic_conditions={
            "Surface Streets": "heavy",
            "Highway 1": "moderate",
        },
        objectives={"priority": "optimize_eta"},
    )

    prop_a = await RouteAgentA().execute(input_data)
    prop_b = await RouteAgentB().execute(input_data)
    classification = await PerceptionAgent().execute(sample_incident)

    sim_input = SimulationInput(
        proposal_a=prop_a, proposal_b=prop_b, incident=classification
    )
    res = await SimulationAgent().execute(sim_input)

    explain_input = ExplainabilityInput(
        negotiation_result=res, proposal_a=prop_a, proposal_b=prop_b
    )

    explain_output = await ExplainabilityAgent().execute(explain_input)
    assert explain_output.approval_required is True
    assert "Surface Streets" in explain_output.decision
    assert "saves ambulance 14 minutes" in explain_output.reasoning_one_liner


@pytest.mark.asyncio
async def test_orchestrator_workflow(sample_incident):
    orchestrator = OrchestratorAgent()
    decision = await orchestrator.execute(sample_incident)

    assert decision.winner == "route_a_speed_first"
    assert decision.requires_approval is True
    assert "Surface Streets" in decision.reasoning_summary
