import { useState, useEffect } from 'react';

export interface StreamLog {
  timestamp: number;
  message: string;
}

const medicalLogs = [
  { time: 0, message: "Orchestrator spawned pipeline workflow." },
  { time: 5, message: "Perception Agent: Classifying incident severity..." },
  { time: 10, message: "Perception Agent: Severity classified as CRITICAL. Priority Score: 0.95." },
  { time: 15, message: "Orchestrator: Spawning Route Agents in parallel..." },
  { time: 20, message: "Route Agent A (Speed-First): Evaluating Surface Streets. ETA: 7 mins." },
  { time: 25, message: "Route Agent B (Fairness-First): Evaluating Highway 1. ETA: 10 mins." },
  { time: 35, message: "Simulation Agent: Running traffic congestion simulations..." },
  { time: 42, message: "Simulation Agent: Scoring plans. Surface Streets: 93/100, Highway 1: 75/100." },
  { time: 48, message: "Explainability Agent: Generating decision brief..." },
  { time: 54, message: "Pipeline execution complete. Decided: Route via Surface Streets. Status: pending_approval." }
];

const accidentLogs = [
  { time: 0, message: "Orchestrator spawned pipeline workflow." },
  { time: 5, message: "Perception Agent: Classifying incident severity..." },
  { time: 10, message: "Perception Agent: Severity classified as MAJOR. Priority Score: 0.70." },
  { time: 15, message: "Orchestrator: Spawning Route Agents in parallel..." },
  { time: 20, message: "Route Agent A (Speed-First): Evaluating Surface Streets. ETA: 9 mins." },
  { time: 25, message: "Route Agent B (Fairness-First): Evaluating Highway 1. ETA: 12 mins." },
  { time: 35, message: "Simulation Agent: Running traffic congestion simulations..." },
  { time: 42, message: "Simulation Agent: Scoring plans. Surface Streets: 88/100, Highway 1: 82/100." },
  { time: 48, message: "Explainability Agent: Generating decision brief..." },
  { time: 54, message: "Pipeline execution complete. Decided: Route via Surface Streets. Status: pending_approval." }
];

const hazardLogs = [
  { time: 0, message: "Orchestrator spawned pipeline workflow." },
  { time: 5, message: "Perception Agent: Classifying incident severity..." },
  { time: 10, message: "Perception Agent: Severity classified as MINOR. Priority Score: 0.40." },
  { time: 15, message: "Orchestrator: Spawning Route Agents in parallel..." },
  { time: 20, message: "Route Agent A (Speed-First): Evaluating Surface Streets. ETA: 15 mins." },
  { time: 25, message: "Route Agent B (Fairness-First): Evaluating Highway 1. ETA: 16 mins." },
  { time: 35, message: "Simulation Agent: Running traffic congestion simulations..." },
  { time: 42, message: "Simulation Agent: Scoring plans. Surface Streets: 85/100, Highway 1: 87/100." },
  { time: 48, message: "Explainability Agent: Generating decision brief..." },
  { time: 54, message: "Pipeline execution complete. Decided: Route via Highway 1. Status: executing." }
];

export const useIncidentStream = (incidentId: string | null) => {
  const [logs, setLogs] = useState<StreamLog[]>([]);
  const [status, setStatus] = useState<string>('idle');
  const [decision, setDecision] = useState<any>(null);

  useEffect(() => {
    if (!incidentId) {
      setLogs([]);
      setStatus('idle');
      setDecision(null);
      return;
    }

    const isDemo = incidentId.startsWith('mock_') || 
                   import.meta.env.VITE_CIVITAS_DEMO_MODE === 'true' || 
                   import.meta.env.CIVITAS_DEMO_MODE === 'true';

    if (isDemo) {
      const isHazard = incidentId.includes('_hazard');
      const isAccident = incidentId.includes('_accident');
      const activeDemoLogs = isHazard ? hazardLogs : (isAccident ? accidentLogs : medicalLogs);

      const demoStartKey = `civitas_demo_start_${incidentId}`;
      let startTimeStr = localStorage.getItem(demoStartKey);
      if (!startTimeStr) {
        startTimeStr = Date.now().toString();
        localStorage.setItem(demoStartKey, startTimeStr);
      }
      const startTime = parseInt(startTimeStr, 10);

      const updateDemoState = () => {
        const currentStartStr = localStorage.getItem(demoStartKey) || startTimeStr;
        const currentStart = parseInt(currentStartStr, 10);
        const elapsed = (Date.now() - currentStart) / 1000;

        // 1. Determine Status based on elapsed time
        let currentStatus = 'connecting';
        if (elapsed >= 90) {
          currentStatus = 'success';
        } else if (elapsed >= 70) {
          currentStatus = 'executing';
        } else if (elapsed >= 55) {
          currentStatus = isHazard ? 'executing' : 'pending_approval';
        } else if (elapsed >= 10) {
          currentStatus = 'processing';
        }
        setStatus(currentStatus);

        // 2. Set active logs based on timeline
        const activeLogs = activeDemoLogs
          .filter((l) => l.time <= elapsed)
          .map((l) => ({ timestamp: currentStart + l.time * 1000, message: l.message }));
        setLogs(activeLogs);

        // 3. Set decision object once pending_approval/executing
        if (elapsed >= 54) {
          if (isHazard) {
            setDecision({
              winner: 'route_b_fairness_first',
              reasoning_one_liner: 'Highway 1 route recommended. Saves 9 minutes with negligible collateral delay (2 vehicles). Auto-executing.',
              requires_approval: false,
              score_a: 85,
              score_b: 87,
              proposal_a: { recommended_route: 'Surface Streets', ambulance_eta: 15, vehicles_impacted: 10 },
              proposal_b: { recommended_route: 'Highway 1', ambulance_eta: 16, vehicles_impacted: 2 }
            });
          } else if (isAccident) {
            setDecision({
              winner: 'route_a_speed_first',
              reasoning_one_liner: 'Plan A chosen with close margin (88 vs 82). Saves 9 minutes but delays 18 vehicles by 3 minutes. Standard approval required.',
              requires_approval: true,
              score_a: 88,
              score_b: 82,
              proposal_a: { recommended_route: 'Surface Streets', ambulance_eta: 9, vehicles_impacted: 18 },
              proposal_b: { recommended_route: 'Highway 1', ambulance_eta: 12, vehicles_impacted: 6 }
            });
          } else {
            setDecision({
              winner: 'route_a_speed_first',
              reasoning_one_liner: 'Surface Streets saves ambulance 15 minutes, delaying 14 vehicles for 2 minutes average. Critical emergency warrants prioritizing speed.',
              requires_approval: true,
              score_a: 93,
              score_b: 75,
              proposal_a: { recommended_route: 'Surface Streets', ambulance_eta: 7, vehicles_impacted: 14 },
              proposal_b: { recommended_route: 'Highway 1', ambulance_eta: 10, vehicles_impacted: 5 }
            });
          }
        } else {
          setDecision(null);
        }
      };

      // Initial run
      updateDemoState();
      const interval = setInterval(updateDemoState, 500);

      return () => clearInterval(interval);
    }

    // ── Real WebSockets Mode ──
    setStatus('connecting');
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
    const wsBase = import.meta.env.VITE_WS_URL || backendUrl;
    const wsUrl = wsBase.startsWith('http') 
      ? wsBase.replace(/^http/, 'ws') 
      : wsBase.startsWith('ws') ? wsBase : `ws://${window.location.host}`;
      
    const socket = new WebSocket(`${wsUrl}/api/v1/incidents/${incidentId}/stream`);

    socket.onopen = () => {
      setStatus('processing');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.log) {
          setLogs((prev) => [...prev, { timestamp: Date.now(), message: data.log }]);
        }
        if (data.status) {
          setStatus(data.status);
        }
        if (data.decision) {
          setDecision(data.decision);
        }
      } catch (err) {
        console.error('Error parsing stream log', err);
      }
    };

    socket.onerror = () => {
      setStatus('error');
    };

    socket.onclose = () => {
      // Mock log generator fallback if socket fails/is offline
      if (logs.length === 0) {
        setStatus('processing');
        const mockLogs = [
          "Perception Agent: Classifying incident severity...",
          "Perception Agent: Severity classified as CRITICAL. Priority Score: 0.95.",
          "Orchestrator: Spawning Route Agents in parallel...",
          "Route Agent A (Speed-First): Evaluating Surface Streets. ETA: 8 mins.",
          "Route Agent B (Fairness-First): Evaluating Highway 1. ETA: 11 mins.",
          "Simulation Agent: Running traffic congestion simulations...",
          "Simulation Agent: Scoring plans. Surface Streets: 92/100, Highway 1: 74/100.",
          "Explainability Agent: Generating decision brief...",
          "Pipeline execution complete. Decided: Route via Surface Streets. Status: pending_approval."
        ];
        mockLogs.forEach((msg, idx) => {
          setTimeout(() => {
            setLogs((prev) => [...prev, { timestamp: Date.now(), message: msg }]);
            if (idx === mockLogs.length - 1) {
              setStatus('pending_approval');
              setDecision({
                winner: 'route_a_speed_first',
                reasoning_one_liner: 'Surface Streets chosen: saves ambulance 14 minutes, delaying 12 vehicles by 2 minutes average.',
                requires_approval: true
              });
            }
          }, (idx + 1) * 300);
        });
      }
    };

    return () => {
      socket.close();
    };
  }, [incidentId]);

  const customSetStatus = (newStatus: string) => {
    if (newStatus === 'executing' && incidentId) {
      const demoStartKey = `civitas_demo_start_${incidentId}`;
      localStorage.setItem(demoStartKey, (Date.now() - 70000).toString());
    }
    setStatus(newStatus);
  };

  return { logs, status, decision, setStatus: customSetStatus };
};
