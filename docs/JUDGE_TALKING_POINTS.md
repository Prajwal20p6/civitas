# CIVITAS — Judge Talking Points

This document provides a guide to panels on each screen, potential questions judges might ask, and recommended answers.

---

## 1. Dashboard Screen

### Q: "Why show a map instead of just data?"
**A**: Traffic is inherently spatial. Public safety dispatchers and city traffic operators think in terms of geographic coordinates, corridors, and intersections, not abstract data columns. Visual mapping speeds up human verification.

### Q: "Is this real data or simulation?"
**A**: The GIS simulation runs on the real-world road grid of Los Angeles. While routing and traffic densities are modeled using public traffic baseline statistics, the AI agent negotiation and decision orchestration are live.

---

## 2. Thought Stream (Terminal View)

### Q: "What's this terminal showing?"
**A**: This is the live, transparent reasoning output of the Google ADK coordination loop. It exposes the step-by-step logic of the underlying agents, ensuring the system never operates as an unexplainable "black box."

### Q: "How many agents are running?"
**A**: Six independent agents run in coordination: Perception classifies the incident, Route Agents A & B generate candidate paths, Simulation scores them in a traffic model, Explainability builds the operator brief, and the Orchestrator sequences the nodes.

---

## 3. Comparison Screen

### Q: "Why do the scores differ (92 vs 74)?"
**A**: They reflect different objective metrics. Route A prioritizes ambulance speed (faster response time), whereas Route B prioritizes city fairness (minimizing civilian queue delays). The scorer weights these based on incident severity.

### Q: "How does the scoring work?"
**A**: It uses a multi-objective formula: ETA optimization (weighted at 40%), civilian traffic impact (30%), and route safety index (30%). The calculation is fully deterministic to ensure predictability.

---

## 4. Heatmaps Tab

### Q: "What am I looking at?"
**A**: These are synthetic congestion matrices predicting queues. Green blocks represent clear, free-flowing intersections; red blocks denote heavily congested hotspots, enabling visual comparison of routes.

---

## 5. Approval Modal

### Q: "Why human approval?"
**A**: Safety-critical systems require human-in-the-loop oversight. If the plan has a high civilian impact (e.g. blocking >10 vehicles), municipal standards dictate that an operator must sign off before signals change.

---

## 6. Execution Screen

### Q: "How fast is the ambulance actually going?"
**A**: The simulation models standard emergency vehicle speeds under active preemption. In the real world, factors like road slope, weather, and pedestrian movement are calculated to adjust the ETA dynamically.

---

## 7. General Questions

### Q: "How is this different from Google Maps?"
**A**: Google Maps identifies path options but cannot change traffic infrastructure. CIVITAS actively coordinates signal arrays to clear paths, negotiating the trade-off between citizen delay and emergency speed.

### Q: "What if both agents are wrong?"
**A**: The operator has full manual override capability. At any point, the dispatcher can bypass AI suggestions and select a manual route or signal preemption pattern directly from the dashboard.

### Q: "How does this scale to large cities?"
**A**: Each city zone or emergency service district runs an independent pair of Route Agents. This keeps execution parallel and fast (on Cloud Run) without bloating the model.

### Q: "Why Gemini instead of ChatGPT?"
**A**: Gemini 2.5 Flash offers superior sub-2-second latency and lower API invocation costs, which is critical for real-time traffic preemption loops where seconds count.

### Q: "What's the cost?"
**A**: Token usage on Gemini 2.5 Flash costs approximately $0.001 per incident. Cloud Run compute costs scale down to zero when no emergencies are active, minimizing municipal operating expenses.

### Q: "Privacy concerns with APIs?"
**A**: None. Incident logs and location data are fully anonymized. No personally identifiable information (PII) is transmitted to the Vertex AI endpoints.

### Q: "What happens if Gemini API is down?"
**A**: The system runs a local offline heuristic fallback and notifies the operator. In demo mode, cached scenario files are loaded automatically to ensure uninterrupted demo capability.
