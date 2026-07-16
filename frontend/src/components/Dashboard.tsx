import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleMapComponent } from './GoogleMapComponent';
import { AgentReasoningStream } from './AgentReasoningStream';
import { ProposalComparison } from './ProposalComparison';
import { SimulationHeatmaps } from './SimulationHeatmaps';
import { ApprovalModal } from './ApprovalModal';
import { ExecutionAnimation } from './ExecutionAnimation';
import { useIncidentStream } from '../hooks/useIncidentStream';
import { api } from '../api/client';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<any[]>([]);
  const [incidentId, setIncidentId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { logs, status, decision, setStatus } = useIncidentStream(incidentId);

  const handleTriggerEmergency = async () => {
    setLoading(true);
    try {
      // Centered on Los Angeles coordinates to align with map center
      const payload = {
        incident_type: 'emergency_911',
        description: 'Cardiac patient dispatch near Los Angeles Downtown Area',
        location: { lat: 34.0522, lng: -118.2437 },
        destination: { name: 'County Hospital', lat: 34.0722, lng: -118.2637 }
      };
      const res = await api.createIncident(payload);
      setIncidentId(res.incident_id);
      
      const newInc = {
        id: res.incident_id,
        location: payload.location,
        status: 'processing'
      };
      setIncidents(prev => [...prev, newInc]);
      navigate(`/incident/${res.incident_id}`);
    } catch (err) {
      console.warn("API Offline. Initializing local mock workflow instead.");
      const mockId = `mock_${Math.random().toString(36).substring(2, 11)}`;
      setIncidentId(mockId);
      
      const newInc = {
        id: mockId,
        location: { lat: 34.0522, lng: -118.2437 },
        status: 'processing'
      };
      setIncidents(prev => [...prev, newInc]);
      navigate(`/incident/${mockId}`);
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
    <div className="min-h-screen bg-white text-slate-800 p-6 flex flex-col gap-6 font-sans selection:bg-blue-500 selection:text-white">
      {/* Top Banner Navigation */}
      <header className="flex justify-between items-center border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <span className="w-4 h-4 bg-blue-600 rounded-full animate-pulse shadow-[0_0_12px_rgba(25,118,210,0.6)]" />
          <h1 className="text-xl font-bold tracking-wider uppercase text-slate-800 font-mono">CIVITAS Traffic Coordinator</h1>
        </div>
        <div className="flex items-center gap-4">
          {incidentId && (
            <div className="bg-slate-100 border border-slate-200 rounded-lg px-3 py-1 font-mono text-xs text-slate-600">
              Session: <span className="text-blue-600 font-bold">{incidentId}</span>
            </div>
          )}
          <button 
            onClick={handleTriggerEmergency}
            disabled={loading || status === 'processing' || status === 'executing'}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-450 text-white text-xs font-semibold uppercase tracking-widest rounded-xl transition-all duration-300 font-mono shadow-sm active:scale-95"
          >
            {loading ? "Triggering..." : "Trigger Emergency"}
          </button>
        </div>
      </header>

      {/* Main Grid Workspace */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* Map Display, Proposals & Heatmaps */}
        <section className="lg:col-span-2 flex flex-col gap-6">
          <GoogleMapComponent status={status} winner={decision?.winner || null} incidents={incidents} />
          
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
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-3 shadow-sm">
              <h3 className="text-xs font-bold text-slate-550 uppercase tracking-widest font-mono">Explainability Output</h3>
              <p className="text-sm leading-relaxed text-slate-700">{decision.reasoning_one_liner}</p>
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
