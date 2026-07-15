import sys
import os
import uuid
from src.adk_setup import SequentialAgent
from src.shared_state import get_session_state
from src.agents.perception import PerceptionAgent
from src.agents.route_agents.speed_first import RouteAgentA
from src.agents.route_agents.fairness_first import RouteAgentB
from src.agents.simulation import SimulationAgent
from src.agents.explainability import ExplainabilityAgent
from src.schemas import IncidentInput, RouteAgentInput, SimulationInput, ExplainabilityInput, OrchestratorDecision

# Dynamically import FirebaseClient from backend sibling directory
try:
    from backend.firebase_client import FirebaseClient
except ImportError:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(base_dir)
    try:
        from backend.firebase_client import FirebaseClient
    except ImportError:
        class FirebaseClient:
            def create_incident(self, incident_id, data): pass
            def update_incident(self, incident_id, data): pass
            def push_reasoning_log(self, incident_id, msg): pass


class OrchestratorAgent(SequentialAgent):
    """
    Orchestrates the full incident response workflow sequentially:
    1. Incident classification via PerceptionAgent
    2. Routing proposals via RouteAgentA & RouteAgentB (executed in parallel)
    3. Simulation scoring & negotiation resolution via SimulationAgent
    4. Natural explanation generation via ExplainabilityAgent
    """
    
    def __init__(self, models: dict = None):
        super().__init__()
        self.state = get_session_state()
        
        # Initialize sub-agents
        self.perception = PerceptionAgent()
        self.route_a = RouteAgentA()
        self.route_b = RouteAgentB()
        self.simulation = SimulationAgent()
        self.explainability = ExplainabilityAgent()
        
        # Initialize database client
        self.db = FirebaseClient()
        
    async def execute(self, incident: IncidentInput, incident_id: str = None) -> OrchestratorDecision:
        """
        Executes the coordinate routing pipeline.
        """
        # Determine unique incident identifier
        i_id = incident_id or getattr(incident, "incident_id", None) or f"incident_{uuid.uuid4().hex[:8]}"
        
        # Step 1: Ingest and Classify Incident
        self.db.push_reasoning_log(i_id, "[Orchestrator] Running Perception Agent classification...")
        classification = await self.perception.execute(incident)
        self.state.write("perception_output", classification.model_dump())
        self.db.update_incident(i_id, {"perception": classification.model_dump()})
        self.db.push_reasoning_log(i_id, f"[Perception] Classified type: {classification.incident_type}, severity: {classification.severity}, priority: {classification.priority_score}")
        
        # Step 2: Generate Proposals from Route Agents A & B (ParallelAgent execution)
        route_input = RouteAgentInput(
            incident_location=incident.location,
            destination={"lat": 37.4280, "lng": -122.0910},
            current_traffic_conditions={"Surface Streets": "heavy", "Highway 1": "moderate"},
            objectives={"priority": "optimize_eta"}
        )
        
        self.db.push_reasoning_log(i_id, "[Orchestrator] Spawning Route Agents A & B in parallel...")
        import asyncio
        task_a = asyncio.create_task(self.route_a.execute(route_input))
        task_b = asyncio.create_task(self.route_b.execute(route_input))
        
        proposal_a, proposal_b = await asyncio.gather(task_a, task_b)
        
        self.state.write("route_a_proposal", proposal_a.model_dump())
        self.state.write("route_b_proposal", proposal_b.model_dump())
        self.db.update_incident(i_id, {
            "route_a_proposal": proposal_a.model_dump(),
            "route_b_proposal": proposal_b.model_dump()
        })
        self.db.push_reasoning_log(i_id, f"[Route Agent A] Recommends: {proposal_a.recommended_route} (ETA: {proposal_a.ambulance_eta} min)")
        self.db.push_reasoning_log(i_id, f"[Route Agent B] Recommends: {proposal_b.recommended_route} (ETA: {proposal_b.ambulance_eta} min)")
        
        # Step 3: Run Simulation and Resolution
        self.db.push_reasoning_log(i_id, "[Orchestrator] Invoking simulation and scoring resolver...")
        sim_input = SimulationInput(
            proposal_a=proposal_a,
            proposal_b=proposal_b,
            incident=classification
        )
        
        negotiation_res = await self.simulation.execute(sim_input)
        self.state.write("negotiation_result", negotiation_res.model_dump())
        self.db.update_incident(i_id, {"negotiation_result": negotiation_res.model_dump()})
        self.db.push_reasoning_log(i_id, f"[Simulation] Resolved winner: {negotiation_res.winner} (Score: {negotiation_res.score_a} vs {negotiation_res.score_b})")
        
        # Step 4: Generate Explainability natural briefs
        self.db.push_reasoning_log(i_id, "[Orchestrator] Compiling decision explanation...")
        explain_input = ExplainabilityInput(
            negotiation_result=negotiation_res,
            proposal_a=proposal_a,
            proposal_b=proposal_b
        )
        explain_output = await self.explainability.execute(explain_input)
        self.state.write("explainability_output", explain_output.model_dump())
        self.db.update_incident(i_id, {"explainability": explain_output.model_dump()})
        self.db.push_reasoning_log(i_id, f"[Explainability] operator Brief: {explain_output.reasoning_one_liner}")
        
        # Set initial approval status
        self.state.write("approval_status", "pending" if explain_output.approval_required else "approved")
        
        return OrchestratorDecision(
            incident_id=i_id,
            proposal_a=proposal_a,
            proposal_b=proposal_b,
            winner=negotiation_res.winner,
            requires_approval=explain_output.approval_required,
            reasoning_summary=explain_output.reasoning_one_liner
        )
