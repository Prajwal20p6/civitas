# CIVITAS — Project State Tracking

This document outlines the current state, progress, confidence metrics, and active blockers for the CIVITAS project.

---

## 1. Project Overview

| Metric | Value |
|---|---|
| **Current Phase** | Phase 1: Setup & Initialization |
| **Current Target Week** | Week 1: Core Agents |
| **System Confidence Score** | **10.0/10.0** (Structured specification created, ready for agent development) |
| **Overall Status** | 🟢 ON TRACK |

---

## 2. Active Focus & Blockers

- **Current Focus**: Initializing the ADK project environment and implementing the Perception Agent parser.
- **Active Blockers**: None.
- **Identified Risks**:
  - *LLM Latency*: Vertex AI Gemini 2.5 API response latency during live demo. Mitigation: Implement pre-seeded deterministic fallback logic.

---

## 3. Component Checklist Status

### A. Agents (`/agents`)
- [x] Folder structure & `.gitkeep` placeholders
- [ ] Perception Agent classification code
- [ ] Route Agent A (Speed-First) routing logic
- [ ] Route Agent B (Fairness-First) routing logic
- [ ] Simulation Agent grid logic
- [ ] Explainability Agent summaries

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
