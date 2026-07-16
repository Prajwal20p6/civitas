# CIVITAS — Pitch & Demo Script (Final)

This document contains the word-for-word presentation script for the CIVITAS live demonstration. It is timed to resolve in exactly **90 seconds**, matching the high-fidelity demo mode.

---

## Pitch Overview
- **Target Duration**: 90 seconds
- **Presenter Role**: City Transportation Chief / AI Architect
- **Goal**: Demonstrate how CIVITAS uses multi-agent negotiation to coordinate emergency routing through congested grids, ensuring human control and zero safety compromises.

---

## Presentation Timeline & Script

### [00:00 - 00:15] Slide / Screen: Dashboard Landing & Problem Introduction
* **Visuals**: Show the *CIVITAS Traffic Coordinator* Light Theme Dashboard. Google Map is centered on Los Angeles with a clean, low-density traffic layout.
* **Script**:
  > "Every second an ambulance is delayed in traffic, the chance of survival decreases by ten percent. Traditional sirens and signal overrides are slow, localized, and cause massive cascading gridlock.
  > 
  > Welcome to CIVITAS: an autonomous emergency traffic coordinator. We use Google ADK multi-agent systems to negotiate priority corridors in real-time, resolving conflicts between speed and urban traffic flow in under 60 seconds."

---

### [00:15 - 00:30] Screen: Triggering Scenario & Perception Classification
* **Visuals**: Click **"Trigger Emergency"** button. The dashboard updates to `Session: mock_xxx`. The live thought stream terminal lights up with log entries:
  * `[Orchestrator] Running Perception Agent...`
  * `[Perception] Classified severity as CRITICAL. Priority: 0.95`
* **Script**:
  > "Let's trigger an emergency scenario. An operator receives a 911 report of a cardiac patient in transit to County Hospital. 
  > 
  > Instantly, our **Perception Agent** ingests the dispatcher's text, classifies it as a critical medical emergency, and assigns a high-priority coefficient of 0.95. This kicks off our parallel routing negotiation."

---

### [00:30 - 00:50] Screen: Competing Proposals & Simulation Heatmaps
* **Visuals**: The live stream logs show route agents proposing routes. Under the **"Comparisons"** and **"Heatmaps"** tabs, the side-by-side proposals and congestion grids render:
  * Plan A (Speed-First) on Surface Streets: 8 min ETA, 12 vehicles impacted (Congestion: 92/100, WINNER).
  * Plan B (Fairness-First) on Highway 1: 11 min ETA, 3 vehicles impacted (Congestion: 74/100).
* **Script**:
  > "The Orchestrator spawns two specialized, competing route agents. **Agent A (Speed-First)** proposes Surface Streets, cutting transit time down to 8 minutes, but impacting 12 civilian vehicles. 
  > 
  > **Agent B (Fairness-First)** proposes Highway 1, taking 11 minutes but disrupting only 3 vehicles. 
  > 
  > Our deterministic **Simulation Engine** runs traffic models. Because this is a critical medical hazard, it decides Plan A achieves the primary objective with acceptable collateral impact, scoring it 92 against Plan B's 74."

---

### [00:50 - 01:10] Screen: Explainability & Operator Approval Modal
* **Visuals**: The dashboard switches to the **"Operator Approval"** tab. The modal dialog overlay pops up: *"Operator Approval Required. Plan A impacts more than 10 vehicles. Please approve green wave preemption sequence."*
* **Script**:
  > "Since this plan has a high impact—disrupting more than 10 vehicles—our **Explainability Agent** marks it for human oversight. It presents a simple, one-sentence brief: *'Surface Streets chosen: saves 14 minutes, delaying 12 vehicles for 2 minutes average.'*
  > 
  > The system pauses. No action is taken until the operator reviews the reasoning and clicks 'Approve Plan'."

---

### [01:10 - 01:30] Screen: Preemption Active & Success Confirmation
* **Visuals**: Click **"Approve Plan"** button. The dashboard navigates to the **"Preemption Active"** tab. The Google Map draws a bright blue preemption path and the ambulance moves in real-time, green wave intersections turning green. The ETA ticks down.
* **At [01:25]**: The progress bar reaches 100%, and the blue **"Preemption Success"** banner pops up at the top: *'Ambulance has arrived safely. Emergency green wave corridor cleared.'*
* **Script**:
  > "Once approved, the **Approval Gate** triggers live preemption. We watch the ambulance advance along the corridor in real-time on our GIS view. Traffic signals ahead of the ambulance are preemptively held green, creating a 'green wave' that sweeps them clear.
  > 
  > Within seconds, the ambulance arrives safely, saving 14 minutes of baseline travel time. The corridor resets automatically, returning control to normal traffic control systems.
  > 
  > That is CIVITAS: autonomous, agentic coordination, guided by human oversight, saving lives in real-time."
