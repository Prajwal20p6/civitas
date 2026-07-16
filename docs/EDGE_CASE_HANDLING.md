# CIVITAS — Edge Case & Demo Failure Recovery Protocol

This document outlines the backup options and troubleshooting protocols if any component fails during the live presentation.

---

## Demo Failure Scenarios & Solutions

### Scenario 1: Map doesn't load / Blank screen
* **Operator Action**:
  * Check console for internet connection status.
  * Say: *"Google Maps API is completing script loading. I will refresh the browser."*
  * If refresh fails, switch to the pre-loaded backup maps presentation on the secondary screen.

---

### Scenario 2: Agent thought stream is empty
* **Operator Action**:
  * Say: *"The ADK workflow is processing the incident context. Let's inspect the Heatmaps tab to view congestion states while they negotiate."*
  * Clicking tabs forces independent re-syncing of Firestore listeners.

---

### Scenario 3: Scores do not appear (Scoring resolver timed out)
* **Operator Action**:
  * Transition immediately to the backup playback video.
  * Say: *"Our real-time scoring engine enforces a strict 3-second deadline to prevent blocking the dispatcher. If it times out, the system defaults to human override. Let's switch to the backup recording to show the optimal path scoring."*

---

### Scenario 4: Approval modal doesn't pop up
* **Operator Action**:
  * Navigate to the **"Operator Approval"** route manually: `http://localhost:3000/incident/{id}/approval`.
  * Say: *"I will open the approval interface directly to clear the corridor."*

---

### Scenario 5: Backend API 500 error
* **Operator Action**:
  * Immediately launch [demo_backup.mp4](file:///e:/civitas/demo_backup.mp4).
  * Say: *"The live coordinator backend has triggered an error boundary. Let's review our recorded high-fidelity verification demo."*

---

### Scenario 6: Internet connection failure
* **Operator Action**:
  * Connect to the backup mobile hotspot.
  * If no cellular signal, launch the offline backup video from the USB drive.

---

## Recovery Protocol Checklist
1. **0 to 15 seconds**: Standard browser reload (`F5` or `Ctrl+F5`).
2. **15 to 30 seconds**: Navigate directly to target screens via sidebar links.
3. **30+ seconds**: Launch [demo_backup.mp4](file:///e:/civitas/demo_backup.mp4).
4. Have the slide URL (pointing to Google Drive / YouTube mirror of the demo video) visible on screen as a final fail-safe.
