# CIVITAS — Project Rules & Guidelines

These are the non-negotiable architectural, coding, and demo design rules for the CIVITAS system.

---

## 1. Architectural Integrity

- **Strict 6-Agent Limit**: The core system is composed of exactly 6 agents:
  1. **Perception Agent** (Gemini 2.5 Flash LLM Classifier)
  2. **Orchestrator Agent** (Gemini 2.5 Pro Sequential Coordinator)
  3. **Route Agent A** (Gemini 2.5 Flash Speed-First Optimization)
  4. **Route Agent B** (Gemini 2.5 Flash Fairness-First Optimization)
  5. **Simulation & Negotiation Agent** (Custom Python Deterministic Scoring Resolver)
  6. **Explainability Agent** (Gemini 2.5 Flash Natural Explanation Generator)
  
- **No Complex Simulators**: Do not integrate heavy third-party simulation tools (e.g., SUMO). Use the custom, lightweight, sub-3-second grid simulation model included in `simulation/`.
- **Firebase/Firestore Split**:
  - Use **Firestore** for transactional state: incidents list, metadata, approvals, and final choices.
  - Use **Firebase Realtime DB** for high-frequency logs: the live agent reasoning and thought streams.
- **Orchestration**: All agents must be defined and executed via the **Google ADK 2.0 Task API** and SequentialAgent/ParallelAgent workflows.

---

## 2. Technical and Coding Standards

- **Strict Type Validation**: All inputs and outputs across all agents must use **Pydantic v2** schemas.
- **Separation of Prompts**: Prompts must be externalized or isolated inside specific agent configuration files (e.g., `prompts.yaml` or static prompt strings at the top of the agent classes), not buried inside business logic.
- **Local Configuration**: Do not commit secrets. Use `.env.example` as the source of truth for the local dev environment, and Google Cloud Secret Manager for production.
- **Execution Performance**:
  - Coordinate pipeline handoffs in under 100ms.
  - Keep agent LLM execution under 3 seconds per agent.
  - Keep grid simulation under 3 seconds.

---

## 3. Demo & Operator UI Rules

- **Deterministic Scenario**: To ensure a flawless demo, there must be a demo-mode toggle in the backend (`DEMO_MODE=true`) which feeds a deterministic set of data and returns a pre-seeded, high-confidence outcome for the 90-second script.
- **Operator Control & Gatekeeping**:
  - The **Human Approval Gate** is mandatory for all high-impact routing decisions (defined as `vehicles_impacted > 10` or `avg_delay_per_vehicle > 4`).
  - Decisions below this threshold must execute automatically, notifying the dashboard.
  - The approval gate has a hard timeout of **30 seconds**. If the operator does not act, the system auto-escalates to emergency mode and overrides signals anyway.
- **Tailwind Aesthetic Constraints**:
  - Use dark mode backgrounds (`bg-gray-950`, `bg-black`) with high-contrast text (`text-green-400`, `text-blue-500`, `text-orange-500`) to highlight live telemetry and simulation heatmap data.
  - Use clean card components for proposals rather than unstructured lists.
