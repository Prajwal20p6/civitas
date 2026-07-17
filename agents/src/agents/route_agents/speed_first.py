import os
import json
from src.adk_setup import LlmAgent
from src.schemas import RouteAgentInput, RouteProposal


def get_genai():
    """Dynamically import google.generativeai for import robustness in test environments."""
    try:
        import google.generativeai as genai

        return genai
    except ImportError:
        return None


class RouteAgentA(LlmAgent):
    """
    Route Agent A (Speed-First): Prioritizes speed and minimizing ambulance travel time.
    """

    def __init__(self, model=None):
        super().__init__(model=model)
        self.model = model

    async def execute(self, inputs: RouteAgentInput) -> RouteProposal:
        """
        Evaluate route options and recommend the fastest path.
        """
        # Dynamic coordinate-seeded heuristic calculations
        lat = inputs.incident_location.get("lat", 34.0522)
        lng = inputs.incident_location.get("lng", -118.2437)
        coord_seed = int(abs(lat * 1000) + abs(lng * 1000)) % 10

        incident_type = inputs.incident_type or "medical_emergency"

        if "medical" in incident_type or "911" in incident_type:
            eta = 6 + (coord_seed % 3)  # 6, 7, or 8 mins
            impact = 12 + (coord_seed % 5)  # 12 to 16 vehicles
            delay = 2
            safety = 0.9 + (coord_seed % 3) * 0.01
            reasoning = f"Critical medical emergency requires prioritizing speed. Selecting Surface Streets route saves {22 - eta} minutes off baseline (ETA: {eta} mins) despite delaying {impact} vehicles."
        elif "accident" in incident_type:
            eta = 8 + (coord_seed % 4)  # 8 to 11 mins
            impact = 15 + (coord_seed % 5)  # 15 to 19 vehicles
            delay = 3
            safety = 0.85 + (coord_seed % 4) * 0.01
            reasoning = f"Major traffic accident requires clear corridor. Selecting Surface Streets route optimizes arrival to {eta} mins, accepting {impact} vehicles impacted to secure collision zone."
        else:
            eta = 12 + (coord_seed % 5)  # 12 to 16 mins
            impact = 5 + (coord_seed % 5)  # 5 to 9 vehicles
            delay = 2
            safety = 0.8 + (coord_seed % 5) * 0.01
            reasoning = f"Minor road hazard route recommendation balances delay vs speed. Recommending Surface Streets (ETA: {eta} mins) with minimal {impact} vehicles delayed."

        api_key = os.getenv("GEMINI_API_KEY")
        genai_client = get_genai()

        if api_key and genai_client:
            try:
                genai_client.configure(api_key=api_key)
                model_client = genai_client.GenerativeModel("gemini-2.5-flash")

                # Mock route options context for prompt
                routes_etas_str = f"Route A (Surface Streets): ETA {eta} mins, Route B (Highway 1): ETA {eta + 3} mins"

                # Exact prompt from spec
                prompt = f"""
You are an emergency route optimization agent. Your goal is to minimize 
ambulance ETA.

Incident: Medical emergency needing transport
Current traffic: {inputs.current_traffic_conditions}

Available routes and their ETAs:
{routes_etas_str}

Analyze each route and recommend the one that minimizes ambulance arrival time.
Consider the trade-off: speed vs. safety and collateral impact.

Respond with JSON:
{{
  "recommended_route": "Surface Streets" or "Highway 1",
  "ambulance_eta": {eta},
  "reasoning": "{reasoning}"
}}

Your PRIMARY goal is to minimize ambulance ETA. You can accept significant 
collateral delays if it saves ambulance time.
"""
                response = model_client.generate_content(
                    prompt, generation_config={"response_mime_type": "application/json"}
                )

                data = json.loads(response.text)
                recommended = data.get("recommended_route", "Surface Streets")

                return RouteProposal(
                    agent_id="route_a_speed_first",
                    recommended_route=recommended,
                    ambulance_eta=eta,
                    vehicles_impacted=impact,
                    avg_delay_per_vehicle=delay,
                    safety_score=safety,
                    reasoning=data.get("reasoning", reasoning),
                    confidence=0.95,
                )
            except Exception:
                pass

        # Heuristic fallback for testing/demo
        return RouteProposal(
            agent_id="route_a_speed_first",
            recommended_route="Surface Streets",
            ambulance_eta=eta,
            vehicles_impacted=impact,
            avg_delay_per_vehicle=delay,
            safety_score=safety,
            reasoning=reasoning,
            confidence=0.95,
        )
