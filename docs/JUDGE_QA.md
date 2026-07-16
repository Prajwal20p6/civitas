# CIVITAS — Judge Q&A Document

This document answers the top 10 potential questions that judges may ask during the pitch presentation.

---

### Q1: "Is this simulation or real data?"
**A**: The GIS map interface runs on the real-world road grid of Los Angeles, mapping real-time preemption corridors. During demo mode, the multi-agent system references seeded incident scenarios, while live mode connects to Vertex AI's real-time LLM agents for live perception, routing decisions, and explainability reasoning.

---

### Q2: "How is this different from Google Maps?"
**A**: Google Maps optimizes route travel times for a single vehicle without altering traffic control infrastructure. CIVITAS actively coordinates urban infrastructure, negotiating signal preemption corridors ("green waves") to prioritize emergency vehicles while dynamically balancing and minimizing collateral delay for the surrounding city traffic.

---

### Q3: "Why two agents with different objectives?"
**A**: Emergency routing has competing priorities: minimizing response times (speed) versus maintaining fair city flow (minimizing civilian blockages). By structuring these as two competing agents—Agent A (Speed-First) and Agent B (Fairness-First)—we capture this trade-off explicitly and resolve it transparently using a deterministic scoring resolver.

---

### Q4: "What's the simulation engine doing?"
**A**: The simulation engine models city intersection queues and traffic flow along the proposed routes in real-time. It calculates expected civilian delays, corridor safety indexes, and ambulance ETAs, feeding these metrics into our multi-objective resolver to compute deterministic scores.

---

### Q5: "How fast is the decision? Latency?"
**A**: In live mode, the entire multi-agent pipeline completes execution in under 1.5 seconds. In deterministic demo mode, results are loaded in under 100 milliseconds to preserve near-zero latency, keeping total dashboard synchronization and streaming logs under 60 seconds.

---

### Q6: "Can this scale to real cities?"
**A**: Yes. By utilizing microservices on Google Cloud Run and communicating via lightweight JSON API endpoints, CIVITAS can be deployed across any urban traffic control network using standardized NTCIP 1202 preemption protocols.

---

### Q7: "What about edge cases / agents disagreeing?"
**A**: If route agents propose vastly different solutions or have close negotiation margins, the system defaults to the deterministic scoring resolver. If the conflict remains highly ambiguous or if the civilian impact exceeds set safety thresholds (>10 vehicles), the Human-in-the-Loop Operator Gate is activated to enforce dispatcher oversight.

---

### Q8: "Why Gemini specifically?"
**A**: We leverage Gemini 2.5 Flash for the routing, perception, and explainability agents due to its extremely low latency and native structured JSON output formatting. For the Orchestrator, we use Gemini 2.5 Pro for complex reasoning and workflow coordination.

---

### Q9: "What's the cost to run this?"
**A**: By utilizing Gemini 2.5 Flash for the majority of LLM calls, token execution costs are under $0.001 per incident. The compute and hosting footprint on Cloud Run scales to zero when inactive, ensuring highly cost-efficient municipal deployments.

---

### Q10: "What's next after the hackathon?"
**A**: We aim to integrate this system with active municipal CAD (Computer-Aided Dispatch) feeds and connect to hardware traffic signal controllers using IoT protocols to conduct pilot tests on a closed-circuit test track.
