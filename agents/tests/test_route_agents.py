import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Retrieve the global mock from conftest
mock_genai = sys.modules["google.generativeai"]


from src.schemas import RouteAgentInput
from src.agents.route_agents.speed_first import RouteAgentA
from src.agents.route_agents.fairness_first import RouteAgentB


@pytest.fixture
def sample_route_input():
    return RouteAgentInput(
        incident_location={"lat": 37.4219, "lng": -122.0840},
        destination={"lat": 37.4280, "lng": -122.0910},
        current_traffic_conditions={
            "Surface Streets": "heavy",
            "Highway 1": "moderate",
        },
        objectives={"priority": "optimize_eta"},
    )


@pytest.mark.asyncio
async def test_route_agents_heuristics(sample_route_input):
    """Verify that both agents return different routes and scores under default heuristics."""
    agent_a = RouteAgentA()
    agent_b = RouteAgentB()

    with patch.dict(os.environ, {}, clear=True):
        prop_a = await agent_a.execute(sample_route_input)
        prop_b = await agent_b.execute(sample_route_input)

        # Verify basic outputs
        assert prop_a.agent_id == "route_a_speed_first"
        assert prop_b.agent_id == "route_b_fairness_first"

        # Verify both agents score and propose differently on same input
        assert prop_a.recommended_route != prop_b.recommended_route
        assert prop_a.ambulance_eta != prop_b.ambulance_eta
        assert prop_a.vehicles_impacted != prop_b.vehicles_impacted
        assert prop_a.avg_delay_per_vehicle != prop_b.avg_delay_per_vehicle


@pytest.mark.asyncio
async def test_route_agents_llm_path(sample_route_input):
    """Verify that route agents make proper LLM calls and parse response fields correctly."""
    agent_a = RouteAgentA()
    agent_b = RouteAgentB()

    # 1. Setup mock response for Agent A
    mock_model_a = MagicMock()
    mock_response_a = MagicMock()
    mock_response_a.text = '{"recommended_route": "Surface Streets", "ambulance_eta": 8, "reasoning": "Fastest route."}'
    mock_model_a.generate_content.return_value = mock_response_a

    # 2. Setup mock response for Agent B
    mock_model_b = MagicMock()
    mock_response_b = MagicMock()
    mock_response_b.text = '{"recommended_route": "Highway 1", "ambulance_eta": 11, "reasoning": "Balanced route."}'
    mock_model_b.generate_content.return_value = mock_response_b

    # Run Agent A and verify
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
        mock_genai.GenerativeModel.return_value = mock_model_a
        prop_a = await agent_a.execute(sample_route_input)
        assert prop_a.recommended_route == "Surface Streets"
        assert prop_a.ambulance_eta == 8
        assert "LLM" not in prop_a.reasoning

        # Run Agent B and verify
        mock_genai.GenerativeModel.return_value = mock_model_b
        prop_b = await agent_b.execute(sample_route_input)
        assert prop_b.recommended_route == "Highway 1"
        assert prop_b.ambulance_eta == 11


@pytest.mark.asyncio
async def test_route_agents_llm_failure_fallback(sample_route_input):
    """Verify that route agents fall back to local heuristics on API errors."""
    agent_a = RouteAgentA()
    agent_b = RouteAgentB()

    # Setup exceptions
    mock_genai.GenerativeModel.side_effect = Exception("API quota exceeded")

    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
        prop_a = await agent_a.execute(sample_route_input)
        prop_b = await agent_b.execute(sample_route_input)

        assert prop_a.recommended_route == "Surface Streets"
        assert prop_a.ambulance_eta == 8

        assert prop_b.recommended_route == "Highway 1"
        assert prop_b.ambulance_eta == 11

    mock_genai.GenerativeModel.side_effect = None
