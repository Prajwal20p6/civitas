from src.adk_setup import SequentialAgent
from src.shared_state import get_session_state
from src.agents.perception import PerceptionAgent
from src.agents.route_agents.speed_first import RouteAgentA
from src.agents.route_agents.fairness_first import RouteAgentB
from src.agents.simulation import SimulationAgent
from src.agents.explainability import ExplainabilityAgent
from src.schemas import IncidentInput, RouteAgentInput, SimulationInput, ExplainabilityInput, OrchestratorDecision

class OrchestratorAgent(SequentialAgent):
    """
    Orchestrates the full incident response workflow sequentially:
    1. Incident classification via PerceptionAgent
    2. Routing proposals via RouteAgentA & RouteAgentB (executed in parallel)
    3. Simulation scoring & negotiation resolution via SimulationAgent
    4. natural explanation generation via ExplainabilityAgent
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
        
    async def execute(self, incident: IncidentInput) -> OrchestratorDecision:
        """
        Executes the coordinate routing pipeline.
        """
        # Step 1: Ingest and Classify Incident
        classification = await self.perception.execute(incident)
        self.state.write("perception_output", classification.model_dump())
        
        # Step 2: Generate Proposals from Route Agents A & B (ParallelAgent execution)
        route_input = RouteAgentInput(
            incident_location=incident.location,
            destination={"lat": 37.4280, "lng": -122.0910},
            current_traffic_conditions={"Surface Streets": "heavy", "Highway 1": "moderate"},
            objectives={"priority": "optimize_eta"}
        )
        print("[Orchestrator] Spawning Route Agents A & B in parallel...")
        import asyncio
        task_a = asyncio.create_task(self.route_a.execute(route_input))
        task_b = asyncio.create_task(self.route_b.execute(route_input))
        
        proposal_a, proposal_b = await asyncio.gather(task_a, task_b)
        
        self.state.write("route_a_proposal", proposal_a.model_dump())
        self.state.write("route_b_proposal", proposal_b.model_dump())


        
        # Step 3: Run Simulation and Resolution
        sim_input = SimulationInput(
            proposal_a=proposal_a,
            proposal_b=proposal_b,
            incident=classification
        )
        
        negotiation_res = await self.simulation.execute(sim_input)
        self.state.write("negotiation_result", negotiation_res.model_dump())
        
        # Step 4: Generate Explainability natural briefs
        explain_input = ExplainabilityInput(
            negotiation_result=negotiation_res,
            proposal_a=proposal_a,
            proposal_b=proposal_b
        )
        explain_output = await self.explainability.execute(explain_input)
        self.state.write("explainability_output", explain_output.model_dump())
        
        # Set initial approval status
        self.state.write("approval_status", "pending" if explain_output.approval_required else "approved")
        
        return OrchestratorDecision(
            incident_id=self.state.incident_id,
            proposal_a=proposal_a,
            proposal_b=proposal_b,
            winner=negotiation_res.winner,
            requires_approval=explain_output.approval_required,
            reasoning_summary=explain_output.reasoning_one_liner
        )

