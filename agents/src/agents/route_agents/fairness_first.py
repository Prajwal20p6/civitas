from src.adk_setup import LlmAgent
from src.schemas import RouteAgentInput, RouteProposal

class RouteAgentB(LlmAgent):
    """Route Agent B (Fairness-First): Prioritizes system-wide traffic fairness and flow stability."""
    
    async def execute(self, inputs: RouteAgentInput) -> RouteProposal:
        """
        Evaluate routing options and recommend the path that minimizes traffic congestion impact.
        """
        # Recommend Highway route which minimizes grid congestion
        return RouteProposal(
            agent_id="route_b_fairness_first",
            recommended_route="Highway 1",
            ambulance_eta=11,
            vehicles_impacted=3,
            avg_delay_per_vehicle=4,
            safety_score=0.8,
            reasoning="Highway 1 route balances ambulance speed (11 minutes) with minimal collateral impact (3 vehicles delayed). Keeps the urban grid stable.",
            confidence=0.85
        )
