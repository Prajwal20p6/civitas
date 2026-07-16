import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Retrieve the global mock from conftest
mock_genai = sys.modules["google.generativeai"]

from src.schemas import (
    RouteProposal,
    IncidentClassification,
    NegotiationResult,
    ExplainabilityInput,
)
from src.agents.explainability import ExplainabilityAgent


@pytest.fixture
def sample_explain_input():
    prop_a = RouteProposal(
        agent_id="route_a_speed_first",
        recommended_route="Surface Streets",
        ambulance_eta=8,
        vehicles_impacted=12,
        avg_delay_per_vehicle=2,
        safety_score=0.9,
        reasoning="Speed optimized path.",
        confidence=0.95,
    )

    prop_b = RouteProposal(
        agent_id="route_b_fairness_first",
        recommended_route="Highway 1",
        ambulance_eta=11,
        vehicles_impacted=3,
        avg_delay_per_vehicle=4,
        safety_score=0.8,
        reasoning="Fairness optimized path.",
        confidence=0.85,
    )

    neg_res = NegotiationResult(
        winner="route_a_speed_first",
        score_a=92.0,
        score_b=74.0,
        margin=18.0,
        reasoning="Speed wins.",
        heatmap_a_url="file:///mock_a.png",
        heatmap_b_url="file:///mock_b.png",
        counterfactual={
            "baseline_eta_no_intervention": 22,
            "planned_eta_with_intervention": 8,
            "time_saved": 14,
        },
    )

    return ExplainabilityInput(
        negotiation_result=neg_res, proposal_a=prop_a, proposal_b=prop_b
    )


@pytest.mark.asyncio
async def test_explainability_heuristics(sample_explain_input):
    """Verify that explainability fallback rules compile correctly."""
    agent = ExplainabilityAgent()

    with patch.dict(os.environ, {}, clear=True):
        # 1. Test when Route A wins
        res_a = await agent.execute(sample_explain_input)
        assert res_a.decision == "Route ambulance via Surface Streets"
        assert "saves ambulance 14 minutes" in res_a.reasoning_one_liner
        assert res_a.approval_required is True

        # 2. Test when Route B wins
        sample_explain_input.negotiation_result.winner = "route_b_fairness_first"
        sample_explain_input.negotiation_result.counterfactual[
            "planned_eta_with_intervention"
        ] = 11

        res_b = await agent.execute(sample_explain_input)
        assert res_b.decision == "Route ambulance via Highway 1"
        assert "minimizes urban impact to 3 vehicles" in res_b.reasoning_one_liner
        assert res_b.approval_required is False


@pytest.mark.asyncio
async def test_explainability_llm_path(sample_explain_input):
    """Verify that the Gemini model is called with correct prompt and formats output."""
    agent = ExplainabilityAgent()

    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Surface Streets chosen: saves 14 mins, delays 12 cars."
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
        res = await agent.execute(sample_explain_input)
        assert res.decision == "Route ambulance via Surface Streets"
        assert (
            res.reasoning_one_liner
            == "Surface Streets chosen: saves 14 mins, delays 12 cars."
        )
        assert res.approval_required is True
        mock_genai.GenerativeModel.assert_called_with("gemini-2.5-flash")
