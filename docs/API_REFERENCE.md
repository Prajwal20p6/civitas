# CIVITAS — API & Database Reference

This document details the FastAPI REST & WebSocket endpoints, data validation schemas, and Firebase structures.

---

## 1. REST & WebSocket Endpoints (FastAPI)

FastAPI runs on port `8000` to serve the React dashboard and trigger ADK workflows.

### Endpoints Overview

| Method | Path | Description | Access |
|---|---|---|---|
| **POST** | `/api/v1/incidents` | Create an incident & invoke Orchestrator | Public |
| **GET** | `/api/v1/incidents/{id}` | Fetch incident status and full decision trace | Public |
| **POST** | `/api/v1/approval/{id}` | Record operator approval/denial | Operator |
| **GET** | `/api/v1/forecast/{zone_id}` | Fetch pre-computed congestion forecast | Public |
| **WS** | `/api/v1/incidents/{id}/stream` | Stream live agent reasoning logs | Public |

---

## 2. Request & Response Schemas

### Create Incident
- **Request Body** (`POST /api/v1/incidents`):
```json
{
  "incident_type": "emergency_911",
  "description": "Ambulance dispatch for cardiac patient",
  "location": {
    "lat": 37.421,
    "lng": -122.084
  },
  "destination": {
    "name": "County General Hospital",
    "lat": 37.428,
    "lng": -122.091
  }
}
```

- **Response Body**:
```json
{
  "incident_id": "incident_4f89d31b",
  "status": "processing",
  "message": "Incident created. ADK Orchestrator invoked."
}
```

### Submit Operator Approval
- **Request Body** (`POST /api/v1/approval/{incident_id}`):
```json
{
  "incident_id": "incident_4f89d31b",
  "status": "approved",
  "reason": "Ambulance speed is paramount; Surface Streets accepted"
}
```

- **Response Body**:
```json
{
  "status": "approved",
  "message": "Approval recorded. Workflow resumed."
}
```

---

## 3. Database Schema Layouts

CIVITAS leverages both Google Firestore and Firebase Realtime Database.

### A. Firestore Collections (Transactional State)

#### Collection: `/incidents`
```json
{
  "incident_id": "incident_4f89d31b",
  "incident_type": "emergency_911",
  "description": "Ambulance dispatch for cardiac patient",
  "status": "pending_approval",  // "processing" | "pending_approval" | "executing" | "completed"
  "location": {
    "lat": 37.421,
    "lng": -122.084
  },
  "destination": {
    "name": "County General Hospital",
    "lat": 37.428,
    "lng": -122.091
  },
  "created_at": "2026-07-15T09:10:09Z",
  "decision": {
    "winner": "agent_a",
    "reasoning_one_liner": "Surface Streets chosen: saves ambulance 3 minutes...",
    "ambulance_eta": 8,
    "vehicles_impacted": 12,
    "avg_delay": 2,
    "score": 92
  }
}
```

#### Sub-collection: `/incidents/{incident_id}/approvals`
```json
{
  "status": "approved",
  "reason": "Approved by operator",
  "approved_at": "2026-07-15T09:10:15Z",
  "expires_at": "2026-07-15T09:10:45Z"
}
```

### B. Realtime Database (High-Frequency Agent Reasoning Logs)

#### Path: `/agents/reasoning/{incident_id}`
```json
{
  "event_001": {
    "timestamp": 0.0,
    "agent": "Perception",
    "emoji": "🚑",
    "message": "Incident ingested: Medical emergency, ETA mismatch."
  },
  "event_002": {
    "timestamp": 0.2,
    "agent": "Perception",
    "emoji": "🧠",
    "message": "Classified severity: CRITICAL. Priority: 0.95."
  },
  "event_003": {
    "timestamp": 0.3,
    "agent": "Orchestrator",
    "emoji": "📋",
    "message": "Spawning speed-first and fairness-first routing agents."
  },
  "event_004": {
    "timestamp": 1.2,
    "agent": "Route Agent A",
    "emoji": "🛣️",
    "message": "Proposing Surface Streets. Est ETA: 8 minutes. Delay: 12 vehicles."
  },
  "event_005": {
    "timestamp": 1.4,
    "agent": "Route Agent B",
    "emoji": "🛣️",
    "message": "Proposing Highway 1. Est ETA: 11 minutes. Delay: 3 vehicles."
  },
  "event_006": {
    "timestamp": 2.0,
    "agent": "Simulation",
    "emoji": "⚖️",
    "message": "Evaluating route grids. Score A: 92/100, Score B: 74/100."
  },
  "event_007": {
    "timestamp": 2.5,
    "agent": "Explainability",
    "emoji": "💬",
    "message": "Drafting operator brief: Route A wins due to life-saving speed."
  }
}
```
