import pytest
import os
import json
import sys
from unittest.mock import MagicMock, patch

# Retrieve the global mock from conftest
mock_genai = sys.modules["google.generativeai"]


# Now import schemas and perception
from src.schemas import IncidentInput
from src.agents.perception import PerceptionAgent

@pytest.fixture
def test_cases():
    fixtures_path = os.path.join("tests", "fixtures", "perception_test_cases.json")
    if not os.path.exists(fixtures_path):
        fixtures_path = os.path.join("agents", "tests", "fixtures", "perception_test_cases.json")
    with open(fixtures_path, "r") as f:
        return json.load(f)

@pytest.mark.asyncio
async def test_perception_heuristics(test_cases):
    """Verify that the rule-based heuristic fallback returns the correct values."""
    agent = PerceptionAgent()
    
    # Temporarily remove GEMINI_API_KEY if present to force heuristics path
    with patch.dict(os.environ, {}, clear=True):
        for case in test_cases:
            incident = IncidentInput(
                incident_type="emergency_911",
                description=case["description"],
                location={"lat": 37.421, "lng": -122.084},
                current_time="2026-07-15T09:30:00Z",
                base_eta_to_destination=20
            )
            
            res = await agent.execute(incident)
            assert res.incident_type == case["expected_type"]
            assert res.severity == case["expected_severity"]
            assert res.priority_score == case["expected_priority"]
            assert len(res.reasoning) > 0

@pytest.mark.asyncio
async def test_perception_llm_path():
    """Verify that the LLM execution path correctly calls google.generativeai and parses response."""
    agent = PerceptionAgent()
    
    incident = IncidentInput(
        incident_type="emergency_911",
        description="Ambulance dispatch for cardiac patient.",
        location={"lat": 37.421, "lng": -122.084},
        current_time="2026-07-15T09:30:00Z",
        base_eta_to_destination=20
    )
    
    # Set up mock response
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"incident_type": "medical_emergency", "severity": "critical", "reasoning": "Stroke patient requires quick routing."}'
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Inject API key and patch the imports/model client
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
        res = await agent.execute(incident)
        
        assert res.incident_type == "medical_emergency"
        assert res.severity == "critical"
        assert res.priority_score == 0.95
        assert res.reasoning == "Stroke patient requires quick routing."
        mock_genai.GenerativeModel.assert_called_with('gemini-2.5-flash')

@pytest.mark.asyncio
async def test_perception_llm_failure_fallback():
    """Verify that if the LLM client call fails, it falls back to heuristics gracefully."""
    agent = PerceptionAgent()
    
    incident = IncidentInput(
        incident_type="emergency_911",
        description="Ambulance dispatch for cardiac patient.",
        location={"lat": 37.421, "lng": -122.084},
        current_time="2026-07-15T09:30:00Z",
        base_eta_to_destination=20
    )
    
    # Set up mock model initialization to raise exception
    mock_genai.GenerativeModel.side_effect = Exception("API limit exceeded")
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
        # Should fallback to rule-based classification automatically
        res = await agent.execute(incident)
        assert res.incident_type == "medical_emergency"
        assert res.severity == "critical"
        assert res.priority_score == 0.95
        assert "emergency" in res.reasoning
        
    # Reset side effect
    mock_genai.GenerativeModel.side_effect = None

