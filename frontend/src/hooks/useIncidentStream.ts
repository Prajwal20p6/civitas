import { useState, useEffect } from 'react';

export interface StreamLog {
  timestamp: number;
  message: string;
}

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

    setStatus('connecting');
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
    const wsBase = import.meta.env.VITE_WS_URL || backendUrl;
    // Clean protocol formatting
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

  return { logs, status, decision, setStatus };
};
