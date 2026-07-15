import pytest
import os
from src.schemas import RouteProposal, IncidentClassification, SimulationInput
from src.agents.simulation import SimulationAgent

@pytest.fixture
def sample_sim_input():
    prop_a = RouteProposal(
        agent_id="route_a_speed_first",
        recommended_route="Surface Streets",
        ambulance_eta=8,
        vehicles_impacted=12,
        avg_delay_per_vehicle=2,
        safety_score=0.9,
        reasoning="Speed optimized path.",
        confidence=0.95
    )
    
    prop_b = RouteProposal(
        agent_id="route_b_fairness_first",
        recommended_route="Highway 1",
        ambulance_eta=11,
        vehicles_impacted=3,
        avg_delay_per_vehicle=4,
        safety_score=0.8,
        reasoning="Fairness optimized path.",
        confidence=0.85
    )
    
    incident = IncidentClassification(
        incident_type="medical_emergency",
        severity="critical",
        location={"lat": 37.421, "lng": -122.084},
        baseline_eta=22,
        priority_score=0.95,
        reasoning="Critical dispatch needed."
    )
    
    return SimulationInput(
        proposal_a=prop_a,
        proposal_b=prop_b,
        incident=incident
    )

@pytest.mark.asyncio
async def test_simulation_resolution(sample_sim_input):
    """Verify that simulation scores and resolves routes, generating visual heatmap files."""
    agent = SimulationAgent()
    res = await agent.execute(sample_sim_input)
    
    # Assert values based on standard scoring formula
    assert res.winner == "route_a_speed_first"
    assert res.score_a == 92.0
    assert res.score_b == 74.0
    assert res.margin == 18.0
    
    # Assert counterfactual values
    assert res.counterfactual["baseline_eta_no_intervention"] == 22
    assert res.counterfactual["planned_eta_with_intervention"] == 8
    assert res.counterfactual["time_saved"] == 14
    
    # Verify file heatmap URLs were generated and files exist
    assert "file:///" in res.heatmap_a_url
    assert "file:///" in res.heatmap_b_url
    
    # Extract file path from file URL and check it exists
    path_a = res.heatmap_a_url.replace("file:///", "")
    path_b = res.heatmap_b_url.replace("file:///", "")
    
    # Resolve drive letter formatting on Windows if necessary
    if ":" in path_a and not path_a.startswith("/"):
        pass
        
    assert os.path.exists(path_a)
    assert os.path.exists(path_b)
    
    # Clean up generated files
    try:
        os.remove(path_a)
        os.remove(path_b)
    except OSError:
        pass
