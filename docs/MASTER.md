# CIVITAS — Master Project Specification

> **The One Sentence Positioning:**
> "CIVITAS is an autonomous emergency traffic coordinator where AI agents negotiate in real-time to create ambulance priority corridors, resolved by simulation scoring and human approval — all in under 60 seconds."

---

## 1. Core Objectives & Positioning

### Why This Works
- **Bounded Scope**: Emergency response represents a highly structured, high-stakes domain with clear optimization rules.
- **AI-Native Story**: Multi-agent conflict resolution (speed vs. fairness) demonstrates true agentic coordination.
- **Autonomous Action**: Real-time traffic signal preemption is simulated and executed.
- **Human-in-the-Loop**: A dedicated operator approval gate ensures safety and production-ready alignment.
- **Rapid Demo**: The entire workflow resolves, simulates, and executes in under 60 seconds.

---

## 2. System Architecture

CIVITAS uses a 6-agent micro-architecture designed to run sequentially and in parallel:

```
┌─────────────────────────────────────────────────────┐
│ INCIDENT TRIGGER (Simulated 911 Call / Sensor)      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  PERCEPTION AGENT        │
        │ (Classify incident)      │
        │ Input: 911 report        │
        │ Output: Critical/Major   │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  ORCHESTRATOR AGENT      │
        │ (Spawn competing agents) │
        │ Input: Incident summary  │
        │ Output: Decision brief   │
        └────┬─────────────────┬───┘
             │                 │
             ▼                 ▼
    ┌─────────────────┐  ┌─────────────────┐
    │  ROUTE AGENT A  │  │  ROUTE AGENT B  │
    │ (Speed-First)   │  │ (Fairness-First)│
    │ Propose: Plan A │  │ Propose: Plan B │
    └────────┬────────┘  └────────┬────────┘
             │                    │
             └────────┬───────────┘
                      ▼
        ┌───────────────────────────┐
        │ SIMULATION + NEGOTIATION  │
        │Score both plans, pick win │
        │Output: Score A vs Score B │
        └──────────────┬────────────┘
                       │
                       ▼
        ┌───────────────────────────┐
        │   EXPLAINABILITY AGENT    │
        │  "Why did Agent A win?"   │
        │Output: One sentence reason│
        └──────────────┬────────────┘
                       │
                       ▼
        ┌───────────────────────────┐
        │   [HUMAN APPROVAL GATE]   │
        │If high-impact: require OK │
        │If low-impact: auto-execute│
        └──────────────┬────────────┘
                       │
                       ▼
        ┌───────────────────────────┐
        │   EXECUTE + DASHBOARD     │
        │  Animate on Google Maps   │
        │Metrics update in real-time│
        └───────────────────────────┘
```

---

## 3. Technology Stack

### Core Technologies
- **Frontend**: React (18.2) + TypeScript + Tailwind CSS (3.3) + Vite (5.0) + Zustand (4.4)
- **Backend**: FastAPI (0.104) + Python (3.11) + Uvicorn
- **AI/LLM Stack**: Google GenAI / Vertex AI (Gemini 2.5 Flash for speed/cost, Gemini 2.5 Pro for Orchestration reasoning)
- **Orchestration**: Google ADK 2.0 (Agent Development Kit)
- **Databases**: Firebase Firestore (incident state/approvals) & Firebase Realtime DB (live agent reasoning stream)
- **Deployment**: Google Cloud Run (backend & agents) + Firebase Hosting (frontend)

---

## 4. Repository Structure

```
civitas/
├── .civitas/                 # Project status and tracking templates
│   ├── PROJECT_STATE.md
│   └── TASKS.md
├── agents/                   # ADK Agents definition
│   ├── perception/           # Incident classification (Flash)
│   ├── orchestrator/         # Sequential workflow coordinator (Pro)
│   ├── route_agents/         # Competitive routing agents (Flash)
│   ├── negotiation/          # Traffic sim & scoring engine (Deterministic)
│   └── explainability/       # Decision naturalizer (Flash)
├── backend/                  # FastAPI Web Gateway
│   ├── api/
│   │   ├── main.py           # REST/WS Server
│   │   └── models.py         # Pydantic Schemas
│   ├── firebase_client.py
│   └── maps_client.py
├── frontend/                 # React client dashboard
│   ├── src/
│   │   ├── components/       # Maps, Stream, Modal UI components
│   │   └── hooks/            # Firebase Realtime DB hooks
│   └── public/
├── deployment/               # Cloud Run, Terraform & Docker configs
├── docs/                     # Technical documentation & reference
├── tests/                    # Integration & validation scripts
└── data/                     # Pre-computed network states & scenarios
```
