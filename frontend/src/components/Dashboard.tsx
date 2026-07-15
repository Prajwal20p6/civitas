import React, { useState } from 'react';
import { GoogleMapComponent } from './GoogleMapComponent';
import { useIncidentStream } from '../hooks/useIncidentStream';
import { api } from '../api/client';

export const Dashboard: React.FC = () => {
  const [incidentId, setIncidentId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { logs, status, decision, setStatus } = useIncidentStream(incidentId);

  const handleTriggerEmergency = async () => {
    setLoading(true);
    try {
      const payload = {
        incident_type: 'emergency_911',
        description: 'Cardiac patient dispatch near Palo Alto University Ave',
        location: { lat: 37.421, lng: -122.084 },
        destination: { name: 'County Hospital', lat: 37.438, lng: -122.143 }
      };
      const res = await api.createIncident(payload);
      setIncidentId(res.incident_id);
    } catch (err) {
      console.warn("API Offline. Initializing local mock workflow instead.");
      // Fallback local UUID to kick off hook's mock timer
      setIncidentId(`mock_${Math.random().toString(36).substr(2, 9)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (approved: boolean) => {
    const act = approved ? 'approved' : 'denied';
    if (incidentId && !incidentId.startsWith('mock_')) {
      try {
        await api.approveIncident(incidentId, approved ? 'approved' : 'denied', "Operator cleared green waves.");
      } catch (err) {
        console.error("Failed to post approval state", err);
      }
    }
    // Update local state directly
    setStatus(approved ? 'executing' : 'denied');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 flex flex-col gap-6 font-sans selection:bg-rose-500 selection:text-white">
      {/* Top Banner Navigation */}
      <header className="flex justify-between items-center border-b border-slate-900 pb-4">
        <div className="flex items-center gap-3">
          <span className="w-4 h-4 bg-rose-500 rounded-full animate-pulse shadow-[0_0_12px_rgba(244,63,94,0.6)]" />
          <h1 className="text-xl font-bold tracking-wider uppercase text-white font-mono">CIVITAS Traffic Coordinator</h1>
        </div>
        <div className="flex items-center gap-4">
          {incidentId && (
            <div className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1 font-mono text-xs text-slate-400">
              Session: <span className="text-rose-400">{incidentId}</span>
            </div>
          )}
          <button 
            onClick={handleTriggerEmergency}
            disabled={loading || status === 'processing' || status === 'executing'}
            className="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-white text-xs font-semibold uppercase tracking-widest rounded-xl transition-all duration-300 font-mono shadow-[0_4px_20px_rgba(225,29,72,0.15)] active:scale-95"
          >
            {loading ? "Triggering..." : "Trigger Emergency"}
          </button>
        </div>
      </header>

      {/* Main Grid Workspace */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* Map Display & Proposals */}
        <section className="lg:col-span-2 flex flex-col gap-6">
          <GoogleMapComponent status={status} winner={decision?.winner || null} />
          
          {/* Side-by-Side Proposal Cards */}
          {decision && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Proposal A: Speed-First */}
              <article className={`p-5 rounded-2xl border transition-all duration-300 ${
                decision.winner === 'route_a_speed_first' 
                  ? 'bg-slate-900/60 border-emerald-500/50 shadow-lg shadow-emerald-500/5' 
                  : 'bg-slate-900/20 border-slate-850 opacity-40'
              }`}>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Plan A (Speed-First)</h3>
                  {decision.winner === 'route_a_speed_first' && (
                    <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-0.5 rounded-full font-bold">WINNER</span>
                  )}
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Route Option:</span>
                    <span className="text-white font-medium">Surface Streets</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Ambulance ETA:</span>
                    <span className="text-emerald-400 font-bold">8 minutes</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Vehicles Impacted:</span>
                    <span className="text-white">12 vehicles</span>
                  </div>
                </div>
              </article>

              {/* Proposal B: Fairness-First */}
              <article className={`p-5 rounded-2xl border transition-all duration-300 ${
                decision.winner === 'route_b_fairness_first' 
                  ? 'bg-slate-900/60 border-emerald-500/50 shadow-lg shadow-emerald-500/5' 
                  : 'bg-slate-900/20 border-slate-850 opacity-40'
              }`}>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Plan B (Fairness-First)</h3>
                  {decision.winner === 'route_b_fairness_first' && (
                    <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-0.5 rounded-full font-bold">WINNER</span>
                  )}
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Route Option:</span>
                    <span className="text-white font-medium">Highway 1</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Ambulance ETA:</span>
                    <span className="text-emerald-400 font-bold">11 minutes</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Vehicles Impacted:</span>
                    <span className="text-white">3 vehicles</span>
                  </div>
                </div>
              </article>
            </div>
          )}
        </section>

        {/* Live Reasoning Terminal Stream */}
        <section className="flex flex-col gap-6">
          <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col gap-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Pipeline Thought Stream</span>
              {status === 'processing' && <span className="animate-pulse text-rose-500 text-[10px] font-bold">● LIVE</span>}
            </div>
            
            <div className="flex-1 overflow-y-auto max-h-[380px] space-y-2.5 font-mono text-xs text-emerald-400 select-text">
              {logs.length === 0 ? (
                <div className="text-slate-600 italic">No incident active. Stream idle.</div>
              ) : (
                logs.map((log, idx) => (
                  <div key={idx} className="flex gap-2 items-start leading-relaxed">
                    <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                    <span>{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
          
          {/* Decision Explanation Display */}
          {decision && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-2xl">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Explainability Output</h3>
              <p className="text-sm leading-relaxed text-slate-200">{decision.reasoning_one_liner}</p>
            </div>
          )}
        </section>
      </main>

      {/* High-Impact Operator Approval Modal Overlay */}
      {status === 'pending_approval' && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-slate-900 border border-rose-500/40 rounded-3xl p-6 max-w-md w-full space-y-5 shadow-2xl shadow-rose-500/10">
            <div className="flex items-center gap-3 text-rose-500">
              <span className="text-2xl">⚠️</span>
              <h3 className="text-md font-bold uppercase tracking-wider font-mono">Operator Approval Required</h3>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              The winning plan (Plan A: Surface Streets) delays more than 10 vehicles. Please approve green wave sequence.
            </p>
            <div className="flex gap-4">
              <button 
                onClick={() => handleApproval(true)}
                className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white text-xs font-bold uppercase tracking-widest rounded-xl transition-all duration-300 font-mono"
              >
                Approve Plan
              </button>
              <button 
                onClick={() => handleApproval(false)}
                className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-300 text-xs font-bold uppercase tracking-widest rounded-xl transition-all duration-300 font-mono"
              >
                Override
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
