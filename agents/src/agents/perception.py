import os
import json
from src.adk_setup import LlmAgent
from src.schemas import IncidentInput, IncidentClassification


def get_genai():
    """Dynamically import google.generativeai for import robustness in test environments."""
    try:
        import google.generativeai as genai

        return genai
    except ImportError:
        return None


class PerceptionAgent(LlmAgent):
    """
    Classifies incoming incident reports to assess severity, type, and urgency.
    """

    def __init__(self, model=None):
        super().__init__(model=model)
        self.model = model

    async def execute(self, incident: IncidentInput) -> IncidentClassification:
        """
        Executes classification using Gemini 2.5 Flash.
        Falls back to rule-based classification if GEMINI_API_KEY is not available.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        genai_client = get_genai()

        if api_key and genai_client:
            try:
                genai_client.configure(api_key=api_key)
                # Initialize Gemini 2.5 Flash model
                model_client = genai_client.GenerativeModel("gemini-2.5-flash")

                # Exact prompt from spec
                prompt = f"""
You are an emergency incident classifier. Analyze the incident and classify it.

Incident: {incident.description}

Respond with JSON:
{{
  "incident_type": "medical_emergency" or "accident" or "hazard",
  "severity": "critical" or "major" or "minor",
  "reasoning": "Why this classification"
}}

Rules:
- Medical emergencies with ETA mismatches are CRITICAL
- Multi-vehicle accidents are MAJOR
- Minor congestion is MINOR
"""
                # Request JSON output
                response = model_client.generate_content(
                    prompt, generation_config={"response_mime_type": "application/json"}
                )

                data = json.loads(response.text)

                severity = data.get("severity", "minor").lower()
                priority_map = {"critical": 0.95, "major": 0.70, "minor": 0.40}
                priority = priority_map.get(severity, 0.40)

                return IncidentClassification(
                    incident_type=data.get("incident_type", "hazard"),
                    severity=severity,
                    location=incident.location,
                    baseline_eta=incident.base_eta_to_destination,
                    priority_score=priority,
                    reasoning=data.get("reasoning", "LLM classified"),
                )
            except Exception:
                # Fallback to heuristics in case of network or API error
                pass

        # Standardized deterministic rule-based heuristics fallback
        desc = incident.description.lower()
        if (
            "cardiac" in desc
            or "stroke" in desc
            or "heart" in desc
            or "ambulance" in desc
            or "patient" in desc
        ):
            inc_type = "medical_emergency"
            severity = "critical"
            priority = 0.95
            reasoning = "High-priority life-threatening medical emergency. Dispatched ambulance requires optimal routing."
        elif "collision" in desc or "accident" in desc or "crash" in desc:
            inc_type = "accident"
            severity = "major"
            priority = 0.70
            reasoning = (
                "Multi-vehicle traffic accident blocking lanes. Elevated risk of delay."
            )
        else:
            inc_type = "hazard"
            severity = "minor"
            priority = 0.40
            reasoning = (
                "Road congestion or minor debris. Routing adjustment recommended."
            )

        return IncidentClassification(
            incident_type=inc_type,
            severity=severity,
            location=incident.location,
            baseline_eta=incident.base_eta_to_destination,
            priority_score=priority,
            reasoning=reasoning,
        )
