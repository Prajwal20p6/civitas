# CIVITAS — Agent Reference Specifications

This document outlines the detailed specifications, inputs, outputs, prompts, and tools for each agent in the CIVITAS coordination pipeline.

---

## 1. Perception Agent (Gemini 2.5 Flash)

- **Purpose**: Ingest incident reports, classify type and severity, and calculate baseline priority.
- **Type**: `LlmAgent`
- **Input Schema**:
```python
from pydantic import BaseModel
from typing import Dict

class IncidentInput(BaseModel):
    incident_type: str  # "emergency_911", "traffic_sensor", "manual_report"
    description: str    # "Ambulance dispatch for cardiac patient near 5th Ave"
    location: Dict[str, float]  # {"lat": 37.421, "lng": -122.084}
    current_time: str   # ISO 8601 string
    base_eta_to_destination: int  # minutes
```

- **Output Schema**:
```python
class IncidentClassification(BaseModel):
    incident_type: str        # "medical_emergency", "accident", "hazard"
    severity: str             # "critical", "major", "minor"
    location: Dict[str, float]
    baseline_eta: int         # minutes without coordination
    priority_score: float     # 0.0 to 1.0
    reasoning: str            # Justification of classification
```

- **System Prompt**:
```python
PERCEPTION_PROMPT = """
You are an emergency incident classifier for CIVITAS. Analyze the input description and determine the severity.

Incident Description: {description}
Base ETA: {base_eta_to_destination}

Classify based on these criteria:
- Medical emergencies with ETA mismatches are CRITICAL
- Multi-vehicle accidents are MAJOR
- Road debris or slow traffic is MINOR

Return JSON representing the IncidentClassification schema.
"""
```

---

## 2. Orchestrator Agent (Gemini 2.5 Pro)

- **Purpose**: Coordinate the execution flow, spawn route proposals in parallel, and route requests to the human gate.
- **Type**: `SequentialAgent` (manages `ParallelAgent` spawning)
- **Input Schema**:
```python
class OrchestratorInput(BaseModel):
    incident_classification: IncidentClassification
    current_city_state: Dict  # Weather, active road closures, construction zones
```

- **Output Schema**:
```python
class OrchestratorDecision(BaseModel):
    incident_id: str
    proposal_a: Dict  # Speed-First Proposal
    proposal_b: Dict  # Fairness-First Proposal
    winner: str       # "agent_a" or "agent_b"
    requires_approval: bool
    reasoning_summary: str
```

- **ADK Workflow Structure (YAML representation)**:
```yaml
name: orchestrator_workflow
agent_type: SequentialAgent
steps:
  - name: receive_incident
    type: read_input
  - name: spawn_route_agents
    type: ParallelAgent
    agents:
      - route_agent_a  # Speed-First
      - route_agent_b  # Fairness-First
  - name: negotiate
    type: invoke_agent
    agent: simulation_negotiation_agent
  - name: verify_approval
    type: conditional
    if: "requires_approval == true"
    then: "human_approval_gate"
    else: "auto_execute"
  - name: explainability
    type: invoke_agent
    agent: explainability_agent
```

---

## 3. Route Agent A: Speed-First (Gemini 2.5 Flash)

- **Purpose**: Propose a route prioritizing the minimization of ambulance travel time.
- **Type**: `LlmAgent`
- **Input Schema**:
```python
class RouteAgentInput(BaseModel):
    incident_location: Dict[str, float]
    destination: Dict[str, float]
    current_traffic_conditions: Dict[str, str]  # {"Main St": "heavy", "I-80": "light"}
```

- **Output Schema**:
```python
class RouteProposal(BaseModel):
    agent_id: str                   # "route_a_speed_first"
    recommended_route: str          # "Surface Streets" or "Highway 1"
    ambulance_eta: int              # minutes
    vehicles_impacted: int          # count of cars delayed at intersections
    avg_delay_per_vehicle: int      # minutes delayed on average
    safety_score: float             # 0.0 to 1.0 (collision risk index)
    reasoning: str
    confidence: float
```

- **System Prompt**:
```python
ROUTE_AGENT_A_PROMPT = """
You are Route Agent A (Speed-First) for CIVITAS.
Your goal is to optimize routing to minimize the ambulance's ETA. You can accept substantial collateral delays for other vehicles to achieve this goal.

Incident Location: {incident_location}
Traffic: {current_traffic_conditions}

Propose the fastest route option. Return JSON matching the RouteProposal schema.
"""
```

---

## 4. Route Agent B: Fairness-First (Gemini 2.5 Flash)

- **Purpose**: Propose a route that balances ambulance speed with minimizing system-wide grid impact.
- **Type**: `LlmAgent`
- **Input Schema**: Same as Route Agent A
- **Output Schema**: Same as Route Agent A (with `agent_id = "route_b_fairness_first"`)
- **System Prompt**:
```python
ROUTE_AGENT_B_PROMPT = """
You are Route Agent B (Fairness-First) for CIVITAS.
Your goal is to balance ambulance travel speed with collateral vehicle impact. Minimize the total delay experienced by non-emergency vehicles and distribute congestion fairly.

Incident Location: {incident_location}
Traffic: {current_traffic_conditions}

Propose a balanced route. Return JSON matching the RouteProposal schema.
"""
```

---

## 5. Simulation & Negotiation Agent (Deterministic Resolver)

- **Purpose**: Evaluate both Route Agent proposals via a deterministic congestion simulation, compute final utility scores, and declare the winner.
- **Type**: Custom Python Script
- **Input Schema**:
```python
class SimulationInput(BaseModel):
    proposal_a: RouteProposal
    proposal_b: RouteProposal
    incident: IncidentClassification
```

- **Output Schema**:
```python
class NegotiationResult(BaseModel):
    winner: str               # "agent_a" or "agent_b"
    score_a: float            # 0.0 to 100.0
    score_b: float            # 0.0 to 100.0
    margin: float
    reasoning: str
    heatmap_a_url: str
    heatmap_b_url: str
    counterfactual: Dict[str, int] # {"baseline_eta": 22, "planned_eta": 8, "time_saved": 14}
```

- **Resolution Scoring Formula**:
$$\text{Score} = 100 - (0.4 \times \text{ETA}) - (0.3 \times \text{Vehicles Impacted}) - (0.3 \times (10 - \text{Safety Score}))$$

---

## 6. Explainability Agent (Gemini 2.5 Flash)

- **Purpose**: Synthesize the negotiation result into a single sentence clear to operators.
- **Type**: `LlmAgent`
- **Input Schema**:
```python
class ExplainabilityInput(BaseModel):
    negotiation_result: NegotiationResult
    proposal_a: RouteProposal
    proposal_b: RouteProposal
```

- **Output Schema**:
```python
class ExplainabilityOutput(BaseModel):
    decision: str              # e.g., "Route ambulance via Surface Streets"
    reasoning_one_liner: str   # "Surface Streets chosen: saves 3 min ambulance ETA with low collateral delays."
    counterfactual: str        # "No action: 22 min. Action: 8 min."
    confidence: float
    approval_required: bool
```

- **System Prompt**:
```python
EXPLAINABILITY_PROMPT = """
Write a ONE SENTENCE summary explaining the decision. It must be clear to a city dispatcher.
Include key metrics: ambulance time saved vs. non-emergency vehicles delayed.

Winner: {winner}
Score: {score_a} vs {score_b}
Reasoning: {reasoning}

Response must match the ExplainabilityOutput JSON structure.
"""
```

---

## 7. Human Approval Gate (ADK Workflow Node)

- **Purpose**: Enforce a safety checkpoint for high-impact plans.
- **Logic**:
  - Activated if: `vehicles_impacted > 10` OR `avg_delay_per_vehicle > 4`.
  - Pause workflow execution.
  - Create incident approval task in Firestore: `status: "pending"`.
  - Subscribe to Firestore updates.
  - Hard timeout: **30 seconds**. If no action occurs, status automatically transitions to `approved_escalated` and executing starts.
