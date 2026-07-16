try:
    from google.agentic.adk import Agent, LlmAgent, SequentialAgent, ParallelAgent
    from google.agentic.adk.models import GeminiModel
    from google.agentic.adk.tools import Tool
except ImportError:
    # Fallback mock classes for local environment dependency safety
    class Agent:
        pass

    class LlmAgent(Agent):
        def __init__(self, model=None):
            self.model = model

    class SequentialAgent(Agent):
        pass

    class ParallelAgent(Agent):
        pass

    class GeminiModel:
        def __init__(self, model_name: str, project: str):
            self.model_name = model_name
            self.project = project

    class Tool:
        pass


try:
    import vertexai
except ImportError:
    # Mock vertexai library
    class MockVertexAI:
        def init(self, project: str, location: str):
            pass

    vertexai = MockVertexAI()


def setup_adk(project_id: str = "civitas-demo"):
    """Initialize ADK runtime and configure agents."""
    vertexai.init(project=project_id, location="us-central1")

    # Define Gemini models
    flash_model = GeminiModel(model_name="gemini-2.5-flash", project=project_id)
    pro_model = GeminiModel(model_name="gemini-2.5-pro", project=project_id)

    return {
        "flash": flash_model,
        "pro": pro_model,
    }


def create_agents(models):
    """Create all agents in the system."""
    from src.agents.perception import PerceptionAgent
    from src.agents.route_agents.speed_first import RouteAgentA
    from src.agents.route_agents.fairness_first import RouteAgentB
    from src.agents.simulation import SimulationAgent
    from src.agents.explainability import ExplainabilityAgent

    perception = PerceptionAgent(model=models["flash"])
    route_a = RouteAgentA(model=models["flash"])
    route_b = RouteAgentB(model=models["flash"])
    simulation = SimulationAgent()  # Custom Python agent
    explainability = ExplainabilityAgent(model=models["flash"])

    return {
        "perception": perception,
        "route_a": route_a,
        "route_b": route_b,
        "simulation": simulation,
        "explainability": explainability,
    }
