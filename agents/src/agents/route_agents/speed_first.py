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
        api_key = os.getenv("GEMINI_API_KEY")
        genai_client = get_genai()
        
        if api_key and genai_client:
            try:
                genai_client.configure(api_key=api_key)
                model_client = genai_client.GenerativeModel('gemini-2.5-flash')
                
                # Mock route options context for prompt
                routes_etas_str = "Route A (Surface Streets): ETA 8 mins, Route B (Highway 1): ETA 11 mins"
                
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
  "ambulance_eta": 8,
  "reasoning": "Minimizes ETA while maintaining safety..."
}}

Your PRIMARY goal is to minimize ambulance ETA. You can accept significant 
collateral delays if it saves ambulance time.
"""
                response = model_client.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                data = json.loads(response.text)
                recommended = data.get("recommended_route", "Surface Streets")
                
                if "highway" in recommended.lower():
                    eta = 11
                    impact = 3
                    delay = 4
                    safety = 0.8
                else:
                    eta = 8
                    impact = 12
                    delay = 2
                    safety = 0.9
                    
                return RouteProposal(
                    agent_id="route_a_speed_first",
                    recommended_route=recommended,
                    ambulance_eta=eta,
                    vehicles_impacted=impact,
                    avg_delay_per_vehicle=delay,
                    safety_score=safety,
                    reasoning=data.get("reasoning", "LLM Speed proposal"),
                    confidence=0.95
                )
            except Exception:
                pass
                
        # Heuristic fallback for testing/demo
        return RouteProposal(
            agent_id="route_a_speed_first",
            recommended_route="Surface Streets",
            ambulance_eta=8,
            vehicles_impacted=12,
            avg_delay_per_vehicle=2,
            safety_score=0.9,
            reasoning="Surface Streets route offers the shortest path and minimizes ambulance ETA to 8 minutes (saving 14 minutes off baseline). Congestion impact is accepted to prioritize life safety.",
            confidence=0.95
        )
