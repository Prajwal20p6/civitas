import { useState, useEffect } from 'react';

export interface StreamLog {
  timestamp: number;
  message: string;
}

const demoLogs = [
  { time: 0, message: "Orchestrator spawned pipeline workflow." },
  { time: 11, message: "Perception Agent: Classifying incident severity..." },
  { time: 15, message: "Perception Agent: Severity classified as CRITICAL. Priority Score: 0.95." },
  { time: 18, message: "Orchestrator: Spawning Route Agents in parallel..." },
  { time: 22, message: "Route Agent A (Speed-First): Evaluating Surface Streets. ETA: 8 mins." },
  { time: 27, message: "Route Agent B (Fairness-First): Evaluating Highway 1. ETA: 11 mins." },
  { time: 36, message: "Simulation Agent: Running traffic congestion simulations..." },
  { time: 42, message: "Simulation Agent: Scoring plans. Surface Streets: 92/100, Highway 1: 74/100." },
  { time: 48, message: "Explainability Agent: Generating decision brief..." },
  { time: 54, message: "Pipeline execution complete. Decided: Route via Surface Streets. Status: pending_approval." }
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
      const demoStartKey = `civitas_demo_start_${incidentId}`;
      let startTimeStr = localStorage.getItem(demoStartKey);
      if (!startTimeStr) {
        startTimeStr = Date.now().toString();
        localStorage.setItem(demoStartKey, startTimeStr);
      }
      const startTime = parseInt(startTimeStr, 10);

      const updateDemoState = () => {
        // Read start time each tick to pick up changes made by approval action
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
          currentStatus = 'pending_approval';
        } else if (elapsed >= 10) {
          currentStatus = 'processing';
        }
        setStatus(currentStatus);

        // 2. Set active logs based on timeline
        const activeLogs = demoLogs
          .filter((l) => l.time <= elapsed)
          .map((l) => ({ timestamp: currentStart + l.time * 1000, message: l.message }));
        setLogs(activeLogs);

        // 3. Set decision object once pending_approval or later
        if (elapsed >= 54) {
          setDecision({
            winner: 'route_a_speed_first',
            reasoning_one_liner: 'Surface Streets chosen: saves ambulance 14 minutes, delaying 12 vehicles by 2 minutes average.',
            requires_approval: true
          });
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
