import os
import json
from src.adk_setup import LlmAgent
from src.schemas import ExplainabilityInput, ExplainabilityOutput


def get_genai():
    """Dynamically import google.generativeai for import robustness in test environments."""
    try:
        import google.generativeai as genai

        return genai
    except ImportError:
        return None


class ExplainabilityAgent(LlmAgent):
    """
    Explainability Agent: Converts the negotiation result into a plain-English justification for city dispatchers.
    """

    def __init__(self, model=None):
        super().__init__(model=model)
        self.model = model

    async def execute(self, inputs: ExplainabilityInput) -> ExplainabilityOutput:
        """
        Translates simulation outcomes and proposals into a natural operator brief using Gemini 2.5 Flash.
        """
        res = inputs.negotiation_result
        winner = res.winner

        api_key = os.getenv("GEMINI_API_KEY")
        genai_client = get_genai()

        if api_key and genai_client:
            try:
                genai_client.configure(api_key=api_key)
                model_client = genai_client.GenerativeModel("gemini-2.5-flash")

                # Exact prompt from spec
                prompt = f"""
Summarize the decision in ONE SENTENCE. Make it clear to a city operator 
why this choice was made.

Winner: {winner}
Score: {res.score_a} vs {res.score_b}
Reasoning: {res.reasoning}

Write ONE sentence that a city operator can understand immediately.
Include the key metric (ambulance ETA saved or impact minimized).

Example: "Surface Streets chosen: saves ambulance 3 minutes, 
impacts 12 vehicles for 2 minutes average."

Your response:
"""
                response = model_client.generate_content(prompt)
                explanation_text = response.text.strip()

                # Map variables
                if winner == "route_a_speed_first":
                    route_name = inputs.proposal_a.recommended_route
                    approval_required = inputs.proposal_a.vehicles_impacted > 10
                else:
                    route_name = inputs.proposal_b.recommended_route
                    approval_required = inputs.proposal_b.vehicles_impacted > 10

                counterfactual = f"Without intervention, ambulance ETA is {res.counterfactual['baseline_eta_no_intervention']} minutes. With chosen plan, ETA is {res.counterfactual['planned_eta_with_intervention']} minutes."

                return ExplainabilityOutput(
                    decision=f"Route ambulance via {route_name}",
                    reasoning_one_liner=explanation_text,
                    counterfactual=counterfactual,
                    confidence=0.92,
                    approval_required=approval_required,
                )
            except Exception:
                pass

        # Rule-based heuristics fallback
        if winner == "route_a_speed_first":
            route_name = inputs.proposal_a.recommended_route
            impact = inputs.proposal_a.vehicles_impacted
            avg_delay = inputs.proposal_a.avg_delay_per_vehicle
            reasoning_one_liner = f"{route_name} chosen: saves ambulance {res.counterfactual['time_saved']} minutes, delaying {impact} vehicles by {avg_delay} minutes average."
            approval_required = True
        else:
            route_name = inputs.proposal_b.recommended_route
            impact = inputs.proposal_b.vehicles_impacted
            avg_delay = inputs.proposal_b.avg_delay_per_vehicle
            reasoning_one_liner = f"{route_name} chosen: minimizes urban impact to {impact} vehicles while delivering ambulance in {inputs.proposal_b.ambulance_eta} minutes."
            approval_required = False

        counterfactual = f"Without intervention, ambulance ETA is {res.counterfactual['baseline_eta_no_intervention']} minutes. With chosen plan, ETA is {res.counterfactual['planned_eta_with_intervention']} minutes."

        return ExplainabilityOutput(
            decision=f"Route ambulance via {route_name}",
            reasoning_one_liner=reasoning_one_liner,
            counterfactual=counterfactual,
            confidence=0.92,
            approval_required=approval_required,
        )
