import os
import sys
import uuid
import asyncio
import logging
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from fastapi import (
    FastAPI,
    BackgroundTasks,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger("civitas.backend")

# Dynamically add agents directory to sys.path to allow sibling imports
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, "agents"))

from src.schemas import IncidentInput
from src.agents.orchestrator import OrchestratorAgent
from backend.firebase_client import FirebaseClient

app = FastAPI(
    title="CIVITAS Emergency Traffic Coordinator Backend",
    version="1.0.0",
    docs_url="/api/docs",
)

from fastapi.staticfiles import StaticFiles

# Enable CORS for React frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/data", StaticFiles(directory=os.path.join(base_dir, "data")), name="data")


# --- Global Error Boundary Middleware ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all error boundary for unhandled exceptions.
    Returns a structured JSON error response instead of crashing.
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. The CIVITAS team has been notified.",
            "detail": str(exc)
            if os.environ.get("CIVITAS_DEBUG", "").lower() == "true"
            else None,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Structured handler for HTTP exceptions (404, 422, etc.)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": f"http_{exc.status_code}", "message": exc.detail},
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
    description: str = Field(
        ..., json_schema_extra={"example": "Ambulance dispatch for cardiac patient"}
    )
    location: LocationSchema
    destination: DestinationSchema


class ApprovalRequest(BaseModel):
    incident_id: str
    status: str = Field(..., json_schema_extra={"example": "approved"})
    reason: str = Field(
        ...,
        json_schema_extra={
            "example": "Ambulance speed is paramount; Surface Streets accepted"
        },
    )


# --- Background Agent Orchestration Task ---
async def execute_orchestration_pipeline(incident_id: str, req: IncidentCreateRequest):
    """
    Background worker that runs the multi-agent decision flow.
    Pushes live stream reasoning updates and writes outcome to DB.

    When CIVITAS_DEMO_MODE=true, uses pre-computed results from
    demo_scenario_final.json instead of calling real LLM agents.
    """
    import time as _time

    try:
        # 1. Update status to processing
        db_client.update_incident(incident_id, {"status": "processing"})
        await manager.broadcast(
            incident_id,
            {"status": "processing", "log": "Orchestrator spawned pipeline workflow."},
        )

        # 2. Emit progressive agent logs for live dashboard UX
        logs = [
            "Perception Agent: Classifying incident severity...",
            "Perception Agent: Severity classified as CRITICAL. Priority Score: 0.95.",
            "Orchestrator: Spawning Route Agents in parallel...",
            "Route Agent A (Speed-First): Evaluating Surface Streets. ETA: 8 mins.",
            "Route Agent B (Fairness-First): Evaluating Highway 1. ETA: 11 mins.",
            "Simulation Agent: Running traffic congestion simulations...",
            "Simulation Agent: Scoring plans. Surface Streets: 92/100, Highway 1: 74/100.",
            "Explainability Agent: Generating decision brief...",
        ]

        for log in logs:
            db_client.push_reasoning_log(incident_id, log)
            await manager.broadcast(incident_id, {"status": "processing", "log": log})
            await asyncio.sleep(0.05)  # small yield to simulate live feed streaming

        # 3. Determine execution mode
        demo_mode = os.environ.get("CIVITAS_DEMO_MODE", "").lower() == "true"

        if demo_mode:
            # ── DEMO MODE: Use pre-computed results, no LLM calls ──
            import json as _json

            demo_path = os.path.join(base_dir, "data", "demo_scenario_final.json")
            with open(demo_path, "r") as f:
                demo = _json.load(f)
            pre = demo["pre_computed_results"]

            # Write all agent outputs to DB
            db_client.update_incident(
                incident_id,
                {
                    "perception": {
                        "incident_type": "medical_emergency",
                        "severity": "critical",
                        "priority_score": 0.95,
                    },
                    "route_a_proposal": pre["route_a_proposal"],
                    "route_b_proposal": pre["route_b_proposal"],
                    "negotiation_result": pre["negotiation_result"],
                    "explainability": pre["explainability"],
                },
            )

            status = "pending_approval"
            db_data = {
                "status": status,
                "decision": {
                    "winner": pre["negotiation_result"]["winner"],
                    "reasoning_one_liner": pre["explainability"]["reasoning_one_liner"],
                    "requires_approval": True,
                    "decision_time_utc": _time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            }
        else:
            # ── LIVE MODE: Run real multi-agent orchestrator pipeline ──
            orchestrator = OrchestratorAgent()
            loc = {"lat": req.location.lat, "lng": req.location.lng}
            incident_in = IncidentInput(
                incident_type=req.incident_type,
                description=req.description,
                location=loc,
                current_time="17:45",
                base_eta_to_destination=22,
            )
            decision = await orchestrator.execute(incident_in)
            status = "pending_approval" if decision.requires_approval else "executing"
            db_data = {
                "status": status,
                "decision": {
                    "winner": decision.winner,
                    "reasoning_one_liner": decision.reasoning_summary,
                    "requires_approval": decision.requires_approval,
                    "decision_time_utc": _time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            }

            # Save intermediate results (especially the 'pending_approval' status) to database
            db_client.update_incident(incident_id, db_data)

            if decision.requires_approval:
                from src.agents.approval_gate import (
                    ApprovalGateAgent,
                    ApprovalGateInput,
                )

                gate_agent = ApprovalGateAgent(db_client=db_client)

                # Fetch perception priority score if present
                inc_record = db_client.get_incident(incident_id) or {}
                perception_data = inc_record.get("perception", {})
                priority_score = perception_data.get("priority_score", 0.95)

                gate_input = ApprovalGateInput(
                    incident_id=incident_id,
                    decision=decision.winner,
                    reasoning=decision.reasoning_summary,
                    impact_score=priority_score,
                    timestamp=_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                )

                gate_result = await gate_agent.execute(gate_input)
                status = (
                    "executing" if gate_result["status"] == "approved" else "denied"
                )
                db_data["status"] = status

        # 4. Save final results to Database
        db_client.update_incident(incident_id, db_data)

        winner_label = db_data["decision"]["winner"].replace("_", " ").title()
        final_log = f"Pipeline execution complete. Decided: Route via {winner_label}. Status: {status}."
        db_client.push_reasoning_log(incident_id, final_log)
        await manager.broadcast(
            incident_id,
            {"status": status, "log": final_log, "decision": db_data["decision"]},
        )

    except Exception as e:
        error_log = f"Pipeline failed with error: {str(e)}"
        db_client.update_incident(incident_id, {"status": "failed", "error": str(e)})
        db_client.push_reasoning_log(incident_id, error_log)
        await manager.broadcast(incident_id, {"status": "failed", "log": error_log})


# --- REST Endpoints ---
@app.get("/api/v1/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "message": "CIVITAS Emergency Traffic Coordinator Backend is healthy.",
    }


@app.post("/api/v1/incidents", status_code=201)
async def create_incident(
    request: IncidentCreateRequest, background_tasks: BackgroundTasks
):
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
            "lng": request.destination.lng,
        },
        "status": "processing",
    }

    # Save metadata to DB
    db_client.create_incident(incident_id, incident_data)

    # Schedule agent execution task in the background
    background_tasks.add_task(execute_orchestration_pipeline, incident_id, request)

    return {
        "incident_id": incident_id,
        "status": "processing",
        "message": "Incident created. ADK Orchestrator invoked.",
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

    db_client.update_incident(
        incident_id,
        {
            "status": status,
            "operator_decision": {
                "status": request.status,
                "reason": request.reason,
                "timestamp": "2026-07-15T09:45:00Z",
            },
        },
    )

    # Push log and broadcast update
    approval_log = f"Operator decision submitted: {request.status.upper()}. Reason: {request.reason}"
    db_client.push_reasoning_log(incident_id, approval_log)
    await manager.broadcast(incident_id, {"status": status, "log": approval_log})

    return {
        "status": request.status,
        "message": f"Approval recorded. Workflow status updated to: {status}.",
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
