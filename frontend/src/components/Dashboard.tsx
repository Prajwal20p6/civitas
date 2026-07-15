import React, { useState } from 'react';
import { GoogleMapComponent } from './GoogleMapComponent';
import { AgentReasoningStream } from './AgentReasoningStream';
import { ProposalComparison } from './ProposalComparison';
import { SimulationHeatmaps } from './SimulationHeatmaps';
import { ApprovalModal } from './ApprovalModal';
import { ExecutionAnimation } from './ExecutionAnimation';
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
      setIncidentId(`mock_${Math.random().toString(36).substring(2, 11)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (approved: boolean) => {
    if (incidentId && !incidentId.startsWith('mock_')) {
      try {
        await api.approveIncident(incidentId, approved ? 'approved' : 'denied', "Operator cleared green waves.");
      } catch (err) {
        console.error("Failed to post approval state", err);
      }
    }
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
        {/* Map Display, Proposals & Heatmaps */}
        <section className="lg:col-span-2 flex flex-col gap-6">
          <GoogleMapComponent status={status} winner={decision?.winner || null} />
          
          <ProposalComparison 
            proposalA={decision ? { recommended_route: 'Surface Streets', ambulance_eta: 8, vehicles_impacted: 12 } : null}
            proposalB={decision ? { recommended_route: 'Highway 1', ambulance_eta: 11, vehicles_impacted: 3 } : null}
            winner={decision?.winner || null}
          />

          <SimulationHeatmaps 
            scoreA={decision ? 92 : null}
            scoreB={decision ? 74 : null}
          />
        </section>

        {/* Live Reasoning Terminal Stream & Animation HUD */}
        <section className="flex flex-col gap-6">
          <AgentReasoningStream logs={logs} status={status} />
          
          <ExecutionAnimation status={status} winner={decision?.winner || null} />

          {/* Decision Explanation Display */}
          {decision && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-2xl">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Explainability Output</h3>
              <p className="text-sm leading-relaxed text-slate-200">{decision.reasoning_one_liner}</p>
            </div>
          )}
        </section>
      </main>

      {/* High-Impact Operator Approval Modal */}
      <ApprovalModal 
        show={status === 'pending_approval'} 
        onApprove={() => handleApproval(true)} 
        onOverride={() => handleApproval(false)} 
      />
    </div>
  );
};
