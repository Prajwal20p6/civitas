import os
from fastapi import FastAPI
from src.agents.orchestrator import OrchestratorAgent
from src.schemas import IncidentInput

app = FastAPI(title="CIVITAS Agents Runtime", version="1.0.0")


@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "civitas-agents-runtime"}


@app.post("/run")
async def run_pipeline(incident: IncidentInput):
    orchestrator = OrchestratorAgent()
    decision = await orchestrator.execute(incident)
    return decision
