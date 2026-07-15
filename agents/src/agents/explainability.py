from src.adk_setup import LlmAgent
from src.schemas import ExplainabilityInput, ExplainabilityOutput

class ExplainabilityAgent(LlmAgent):
    """Explainability Agent: Translates negotiation outcome into a plain-English explanation for city dispatchers."""
    
    async def execute(self, inputs: ExplainabilityInput) -> ExplainabilityOutput:
        """
        Synthesize simulation and routing inputs into operator-friendly briefings.
        """
        res = inputs.negotiation_result
        winner = res.winner
        
        # Construct summary outputs
        if winner == "route_a_speed_first":
            route_name = inputs.proposal_a.recommended_route
            eta = inputs.proposal_a.ambulance_eta
            impact = inputs.proposal_a.vehicles_impacted
            avg_delay = inputs.proposal_a.avg_delay_per_vehicle
            reasoning_one_liner = f"{route_name} chosen: saves ambulance {res.counterfactual['time_saved']} minutes, delaying {impact} vehicles by {avg_delay} minutes average."
            approval_required = True  # High impact (>10 vehicles)
        else:
            route_name = inputs.proposal_b.recommended_route
            eta = inputs.proposal_b.ambulance_eta
            impact = inputs.proposal_b.vehicles_impacted
            avg_delay = inputs.proposal_b.avg_delay_per_vehicle
            reasoning_one_liner = f"{route_name} chosen: minimizes urban impact to {impact} vehicles while delivering ambulance in {eta} minutes."
            approval_required = False
            
        counterfactual = f"Without intervention, ambulance ETA is {res.counterfactual['baseline_eta_no_intervention']} minutes. With chosen plan, ETA is {res.counterfactual['planned_eta_with_intervention']} minutes."
        
        return ExplainabilityOutput(
            decision=f"Route ambulance via {route_name}",
            reasoning_one_liner=reasoning_one_liner,
            counterfactual=counterfactual,
            confidence=0.92,
            approval_required=approval_required
        )
