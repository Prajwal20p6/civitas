# CIVITAS — Weekly Task List

This is the task tracking checklist for the 4-week build cycle. Use this document to update task states (`[ ]` to `[/]` to `[x]`).

---

## Week 1: Core Agent Functionality
- [x] Create project directory structure & initialize git repository
- [x] Configure `.gitignore` with ignore patterns
- [x] Create core documentation files (`MASTER.md`, `PROJECT_RULES.md`, `DEVELOPMENT_PLAN.md`, etc.)
- [x] Initialize ADK project environment & configure dependency files (`pyproject.toml`)
- [x] Implement **Perception Agent** class for incident parsing (Gemini Flash)
- [x] Implement **Route Agent A** class for speed-first proposals (Gemini Flash)
- [x] Implement **Route Agent B** class for fairness-first proposals (Gemini Flash)
- [x] Implement **Google Maps API Integration** helper script
- [x] Build **Simulation Engine** road network grid code (`traffic_model.py`)
- [x] Implement deterministic resolver and scoring equation (`resolver.py`)
- [x] Implement **Explainability Agent** class (Gemini Flash)
- [x] Write CLI execution test runner script (`cli.py`)
- [x] Write agent basic unit tests


---

## Week 2: Simulation & Integration
- [x] Optimize simulation performance to run under 3 seconds
- [x] Implement visual heatmap renderer output (SVG/PNG)
- [x] Design and implement **ADK Workflow Human Approval Gate** node
- [x] Implement global shared session state manager
- [x] Integrate Firebase Firestore & Realtime DB SDKs in backend helper
- [x] Create deterministic scenario dataset for demo-mode reproducibility
- [x] Write integration test scripts validating Firestore state transitions

---

## Week 3: Frontend & Google Integrations
- [x] Initialize Vite + TypeScript React client application
- [x] Build layout and incident logger sidebar components
- [x] Integrate Google Maps JS SDK map views and path tracking
- [x] Develop live agent thought stream terminal emulator UI component
- [x] Create proposal cards comparison component
- [x] Develop high-impact Operator Approval modal overlay
- [x] Complete FastAPI backend routing logic and Websocket connections
- [x] Wire up dashboard to backend WebSockets and Firestore listeners

---

## Week 4: Polish, Deployment & Demo
- [x] Implement final bug fixes and handle backend error boundaries
- [x] Configure `Dockerfile` containers for backend and agents
- [x] Deploy backend API and ADK agents to Google Cloud Run (Configured in deployment/)
- [x] Deploy frontend static assets to Firebase Hosting (Configured in frontend/firebase.json)
- [x] Setup GCP Cloud Build pipeline triggers for CI/CD automation
- [x] Record high-quality 90-second backup demo video (`demo_backup.mp4`)
- [x] Write word-for-word pitch presentation script (`DEMO_SCRIPT_FINAL.md`)
- [x] Rehearse live demonstration flow (target: <2 minutes execution)
