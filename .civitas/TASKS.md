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
- [ ] Optimize simulation performance to run under 3 seconds
- [ ] Implement visual heatmap renderer output (SVG/PNG)
- [ ] Design and implement **ADK Workflow Human Approval Gate** node
- [ ] Implement global shared session state manager
- [ ] Integrate Firebase Firestore & Realtime DB SDKs in backend helper
- [ ] Create deterministic scenario dataset for demo-mode reproducibility
- [ ] Write integration test scripts validating Firestore state transitions

---

## Week 3: Frontend & Google Integrations
- [ ] Initialize Vite + TypeScript React client application
- [ ] Build layout and incident logger sidebar components
- [ ] Integrate Google Maps JS SDK map views and path tracking
- [ ] Develop live agent thought stream terminal emulator UI component
- [ ] Create proposal cards comparison component
- [ ] Develop high-impact Operator Approval modal overlay
- [ ] Complete FastAPI backend routing logic and Websocket connections
- [ ] Wire up dashboard to backend WebSockets and Firestore listeners

---

## Week 4: Polish, Deployment & Demo
- [ ] Implement final bug fixes and handle backend error boundaries
- [ ] Configure `Dockerfile` containers for backend and agents
- [ ] Deploy backend API and ADK agents to Google Cloud Run
- [ ] Deploy frontend static assets to Firebase Hosting
- [ ] Setup GCP Cloud Build pipeline triggers for CI/CD automation
- [ ] Record high-quality 90-second backup demo video (`demo_backup.mp4`)
- [ ] Write word-for-word pitch presentation script (`DEMO_SCRIPT_FINAL.md`)
- [ ] Rehearse live demonstration flow (target: <2 minutes execution)
