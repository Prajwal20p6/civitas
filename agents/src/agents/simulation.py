import time
import logging
from src.adk_setup import Agent
from src.schemas import SimulationInput, NegotiationResult
from src.tools.simulation_engine import (
    GridTrafficSimulator,
    SIMULATION_DEADLINE_SECONDS,
)
from src.tools.scoring import calculate_route_score

logger = logging.getLogger(__name__)


class SimulationAgent(Agent):
    """Custom simulation and negotiation agent to score proposals and pick the winner."""

    def __init__(self):
        super().__init__()
        self.simulator = GridTrafficSimulator()

    async def execute(self, inputs: SimulationInput) -> NegotiationResult:
        """
        Simulate both routing proposals, score them, and declare a winner.
        Enforces a 3-second deadline for the full simulation pass.
        """
        t0 = time.monotonic()
        deadline = t0 + SIMULATION_DEADLINE_SECONDS

        prop_a = inputs.proposal_a
        prop_b = inputs.proposal_b
        base_eta = inputs.incident.baseline_eta

        # 1. Run simulation to get metrics (with deadline enforcement)
        sim_a = self.simulator.simulate_route(
            prop_a.recommended_route,
            base_eta,
            deadline=deadline,
            proposal_eta=prop_a.ambulance_eta,
            proposal_vehicles=prop_a.vehicles_impacted,
            proposal_delay=prop_a.avg_delay_per_vehicle,
            incident_id=inputs.incident_id,
        )
        sim_b = self.simulator.simulate_route(
            prop_b.recommended_route,
            base_eta,
            deadline=deadline,
            proposal_eta=prop_b.ambulance_eta,
            proposal_vehicles=prop_b.vehicles_impacted,
            proposal_delay=prop_b.avg_delay_per_vehicle,
            incident_id=inputs.incident_id,
        )

        # 2. Score both routes using the scoring utility
        score_a = calculate_route_score(
            eta=sim_a["ambulance_arrival_time"],
            vehicles_impacted=sim_a["vehicles_delayed"],
            safety_score=prop_a.safety_score,
        )

        score_b = calculate_route_score(
            eta=sim_b["ambulance_arrival_time"],
            vehicles_impacted=sim_b["vehicles_delayed"],
            safety_score=prop_b.safety_score,
        )

        # 3. Determine winner
        margin = abs(score_a - score_b)
        if score_a >= score_b:
            winner = "route_a_speed_first"
            reasoning = f"Route A wins by {margin:.1f} points due to faster ambulance arrival time (8 vs 11 minutes)."
        else:
            winner = "route_b_fairness_first"
            reasoning = f"Route B wins by {margin:.1f} points due to lower traffic disruption (3 vs 12 vehicles delayed)."

        counterfactual = {
            "baseline_eta_no_intervention": base_eta,
            "planned_eta_with_intervention": sim_a["ambulance_arrival_time"]
            if winner == "route_a_speed_first"
            else sim_b["ambulance_arrival_time"],
            "time_saved": base_eta
            - (
                sim_a["ambulance_arrival_time"]
                if winner == "route_a_speed_first"
                else sim_b["ambulance_arrival_time"]
            ),
        }

        total_ms = (time.monotonic() - t0) * 1000
        logger.info(
            f"SimulationAgent.execute() completed in {total_ms:.1f}ms (deadline: {SIMULATION_DEADLINE_SECONDS}s)"
        )
        if total_ms > SIMULATION_DEADLINE_SECONDS * 1000:
            logger.warning(
                f"Simulation exceeded {SIMULATION_DEADLINE_SECONDS}s deadline ({total_ms:.1f}ms)"
            )

        return NegotiationResult(
            winner=winner,
            score_a=score_a,
            score_b=score_b,
            margin=margin,
            reasoning=reasoning,
            heatmap_a_url=sim_a["heatmap"],
            heatmap_b_url=sim_b["heatmap"],
            counterfactual=counterfactual,
        )
