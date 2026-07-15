# CIVITAS — Project State Tracking

This document outlines the current state, progress, confidence metrics, and active blockers for the CIVITAS project.

---

## 1. Project Overview

| Metric | Value |
|---|---|
| **Current Phase** | Phase 2: Simulation & Integration |
| **Current Target Week** | Week 2: Integration & Backend Gateway |
| **System Confidence Score** | **10.0/10.0** (Week 1 core agents fully implemented, tested, and passing) |
| **Overall Status** | 🟢 ON TRACK |

---

## 2. Active Focus & Blockers

- **Current Focus**: Setting up the FastAPI backend endpoints, Firebase client integrations, and human approval node logic.
- **Active Blockers**: None.
- **Identified Risks**:
  - *LLM Latency*: Vertex AI Gemini 2.5 API response latency during live demo. Mitigation: Implement pre-seeded deterministic fallback logic.

---

## 3. Component Checklist Status

### A. Agents (`/agents`)
- [x] Folder structure & `.gitkeep` placeholders
- [x] Perception Agent classification code
- [x] Route Agent A (Speed-First) routing logic
- [x] Route Agent B (Fairness-First) routing logic
- [x] Simulation Agent grid logic
- [x] Explainability Agent summaries


### B. Backend Gateways (`/backend`)
- [x] Directory initialization
- [ ] FastAPI endpoints setup
- [ ] WebSocket event dispatcher
- [ ] Firebase Firestore client
- [ ] Firebase Realtime DB listener

### C. Frontend Dashboard (`/frontend`)
- [x] Directory initialization
- [ ] Google Maps component mounting
- [ ] Real-time WebSocket thought stream console
- [ ] Proposal side-by-side card layouts
- [ ] Live operator approval dialog modal

### D. Deployments (`/deployment`)
- [x] Directory initialization
- [ ] Cloud Run container Dockerfile
- [ ] Firebase Hosting config
- [ ] Google Cloud Build CI/CD YAML
