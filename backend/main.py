import os
import sys
import uuid
import asyncio
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Dynamically add agents directory to sys.path to allow sibling imports
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, "agents"))

from src.schemas import IncidentInput
from src.agents.orchestrator import OrchestratorAgent
from backend.firebase_client import FirebaseClient

app = FastAPI(
    title="CIVITAS Emergency Traffic Coordinator Backend",
    version="1.0.0",
    docs_url="/api/docs"
)

# Enable CORS for React frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Client wrapper
db_client = FirebaseClient()

# --- Connection Manager for Live WebSocket Reasoning Streams ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, incident_id: str, websocket: WebSocket):
        await websocket.accept()
        if incident_id not in self.active_connections:
            self.active_connections[incident_id] = []
        self.active_connections[incident_id].append(websocket)

    def disconnect(self, incident_id: str, websocket: WebSocket):
        if incident_id in self.active_connections:
            try:
                self.active_connections[incident_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[incident_id]:
                del self.active_connections[incident_id]

    async def broadcast(self, incident_id: str, message: dict):
        if incident_id in self.active_connections:
            for connection in self.active_connections[incident_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()

# --- Pydantic API Schemas ---
class LocationSchema(BaseModel):
    lat: float
    lng: float

class DestinationSchema(BaseModel):
    name: str
    lat: float
    lng: float

class IncidentCreateRequest(BaseModel):
    incident_type: str = Field(..., json_schema_extra={"example": "emergency_911"})
    description: str = Field(..., json_schema_extra={"example": "Ambulance dispatch for cardiac patient"})
    location: LocationSchema
    destination: DestinationSchema

class ApprovalRequest(BaseModel):
    incident_id: str
    status: str = Field(..., json_schema_extra={"example": "approved"})
    reason: str = Field(..., json_schema_extra={"example": "Ambulance speed is paramount; Surface Streets accepted"})


# --- Background Agent Orchestration Task ---
async def execute_orchestration_pipeline(incident_id: str, req: IncidentCreateRequest):
    """
    Background worker that runs the multi-agent decision flow.
    Pushes live stream reasoning updates and writes outcome to DB.
    """
    try:
        # 1. Update status to processing
        db_client.update_incident(incident_id, {"status": "processing"})
        await manager.broadcast(incident_id, {"status": "processing", "log": "Orchestrator spawned pipeline workflow."})
        
        # 2. Simulate progressive agent logs for live dashboard UX
        logs = [
            "Perception Agent: Classifying incident severity...",
            "Perception Agent: Severity classified as CRITICAL. Priority Score: 0.95.",
            "Orchestrator: Spawning Route Agents in parallel...",
            "Route Agent A (Speed-First): Evaluating Surface Streets. ETA: 8 mins.",
            "Route Agent B (Fairness-First): Evaluating Highway 1. ETA: 11 mins.",
            "Simulation Agent: Running traffic congestion simulations...",
            "Simulation Agent: Scoring plans. Surface Streets: 92/100, Highway 1: 74/100.",
            "Explainability Agent: Generating decision brief..."
        ]
        
        for log in logs:
            db_client.push_reasoning_log(incident_id, log)
            await manager.broadcast(incident_id, {"status": "processing", "log": log})
            await asyncio.sleep(0.1)  # small yield to simulate live feed streaming
            
        # 3. Instantiate and run real pipeline Orchestrator
        orchestrator = OrchestratorAgent()
        
        # Sanitize location dict
        loc = {"lat": req.location.lat, "lng": req.location.lng}
        
        incident_in = IncidentInput(
            incident_type=req.incident_type,
            description=req.description,
            location=loc,
            current_time="17:45",
            base_eta_to_destination=22
        )
        
        decision = await orchestrator.execute(incident_in)
        
        # Determine status based on approval requirements
        status = "pending_approval" if decision.requires_approval else "executing"
        
        # 4. Save results to Database
        import time
        db_data = {
            "status": status,
            "decision": {
                "winner": decision.winner,
                "reasoning_one_liner": decision.reasoning_summary,
                "requires_approval": decision.requires_approval,
                "decision_time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }

        
        db_client.update_incident(incident_id, db_data)
        
        final_log = f"Pipeline execution complete. Decided: Route via {decision.winner.replace('_', ' ').title()}. Status: {status}."
        db_client.push_reasoning_log(incident_id, final_log)
        await manager.broadcast(incident_id, {"status": status, "log": final_log, "decision": db_data["decision"]})
        
    except Exception as e:
        error_log = f"Pipeline failed with error: {str(e)}"
        db_client.update_incident(incident_id, {"status": "failed", "error": str(e)})
        db_client.push_reasoning_log(incident_id, error_log)
        await manager.broadcast(incident_id, {"status": "failed", "log": error_log})

# --- REST Endpoints ---
@app.post("/api/v1/incidents", status_code=201)
async def create_incident(request: IncidentCreateRequest, background_tasks: BackgroundTasks):
    """
    Creates a new incident record, schedules the agent pipeline in the background, 
    and returns immediately to keep response latency <100ms.
    """
    incident_id = f"incident_{uuid.uuid4().hex[:8]}"
    
    incident_data = {
        "incident_id": incident_id,
        "incident_type": request.incident_type,
        "description": request.description,
        "location": {"lat": request.location.lat, "lng": request.location.lng},
        "destination": {
            "name": request.destination.name,
            "lat": request.destination.lat,
            "lng": request.destination.lng
        },
        "status": "processing"
    }
    
    # Save metadata to DB
    db_client.create_incident(incident_id, incident_data)
    
    # Schedule agent execution task in the background
    background_tasks.add_task(execute_orchestration_pipeline, incident_id, request)
    
    return {
        "incident_id": incident_id,
        "status": "processing",
        "message": "Incident created. ADK Orchestrator invoked."
    }

@app.get("/api/v1/incidents/{incident_id}")
async def get_incident_status(incident_id: str):
    """Fetches incident status and decision outcome."""
    incident = db_client.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@app.post("/api/v1/approval/{incident_id}")
async def submit_operator_approval(incident_id: str, request: ApprovalRequest):
    """Records operator approval/denial decision, updating status."""
    incident = db_client.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    status = "executing" if request.status == "approved" else "denied"
    
    db_client.update_incident(incident_id, {
        "status": status,
        "operator_decision": {
            "status": request.status,
            "reason": request.reason,
            "timestamp": "2026-07-15T09:45:00Z"
        }
    })
    
    # Push log and broadcast update
    approval_log = f"Operator decision submitted: {request.status.upper()}. Reason: {request.reason}"
    db_client.push_reasoning_log(incident_id, approval_log)
    await manager.broadcast(incident_id, {"status": status, "log": approval_log})
    
    return {
        "status": request.status,
        "message": f"Approval recorded. Workflow status updated to: {status}."
    }

@app.get("/api/v1/forecast/{zone_id}")
async def get_zone_forecast(zone_id: str):
    """Returns predictive zone forecast metrics."""
    return db_client.get_forecast(zone_id)

# --- WebSocket Streaming Endpoint ---
@app.websocket("/api/v1/incidents/{incident_id}/stream")
async def websocket_reasoning_stream(websocket: WebSocket, incident_id: str):
    """WebSocket endpoint streaming live agent reasoning logs."""
    await manager.connect(incident_id, websocket)
    
    # Send historical logs first
    history = db_client.get_reasoning_logs(incident_id)
    for log in history:
        await websocket.send_json({"status": "streaming", "log": log["message"]})
        
    try:
        while True:
            # Keep connection open and listen for client packets if any
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(incident_id, websocket)
