import React from 'react';
import { useParams } from 'react-router-dom';
import { useFirestore } from '../hooks/useFirestore';

export interface RouteProposal {
  recommended_route: string;
  ambulance_eta: number;
  vehicles_impacted: number;
  avg_delay_per_vehicle?: number;
  safety_score?: number;
  reasoning?: string;
}

interface ProposalComparisonProps {
  proposalA?: RouteProposal | null;
  proposalB?: RouteProposal | null;
  winner?: string | null;
}

export const ProposalComparison: React.FC<ProposalComparisonProps> = ({ 
  proposalA: propProposalA, 
  proposalB: propProposalB, 
  winner: propWinner 
}) => {
  const { id } = useParams<{ id: string }>();
  const { incidentData } = useFirestore(propProposalA ? null : (id || null));

  // Determine active state and data fallbacks
  const isActive = !!id || !!propProposalA;
  if (!isActive) return null;

  const proposalA = propProposalA || incidentData?.route_a_proposal || (id ? { recommended_route: 'Surface Streets', ambulance_eta: 8, vehicles_impacted: 12 } : null);
  const proposalB = propProposalB || incidentData?.route_b_proposal || (id ? { recommended_route: 'Highway 1', ambulance_eta: 11, vehicles_impacted: 3 } : null);
  const winner = propWinner || incidentData?.decision?.winner || incidentData?.negotiation_result?.winner || (id ? 'route_a_speed_first' : null);

  if (!proposalA || !proposalB) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Proposal A: Speed-First */}
      <article className={`p-5 rounded-2xl border transition-all duration-300 ${
        winner === 'route_a_speed_first' 
          ? 'bg-slate-50 border-blue-600 shadow-md' 
          : 'bg-slate-50/50 border-slate-200 opacity-60'
      }`}>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono">Plan A (Speed-First)</h3>
          {winner === 'route_a_speed_first' && (
            <span className="bg-blue-100 text-blue-805 border border-blue-200 text-[10px] px-2 py-0.5 rounded-full font-bold">WINNER</span>
          )}
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500 font-sans">Route Option:</span>
            <span className="text-slate-800 font-semibold">{proposalA.recommended_route}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 font-sans">Ambulance ETA:</span>
            <span className="text-blue-600 font-bold">{proposalA.ambulance_eta} mins</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 font-sans">Vehicles Impacted:</span>
            <span className="text-slate-800">{proposalA.vehicles_impacted} vehicles</span>
          </div>
        </div>
      </article>

      {/* Proposal B: Fairness-First */}
      <article className={`p-5 rounded-2xl border transition-all duration-300 ${
        winner === 'route_b_fairness_first' 
          ? 'bg-slate-50 border-blue-600 shadow-md' 
          : 'bg-slate-50/50 border-slate-200 opacity-60'
      }`}>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono">Plan B (Fairness-First)</h3>
          {winner === 'route_b_fairness_first' && (
            <span className="bg-blue-100 text-blue-805 border border-blue-200 text-[10px] px-2 py-0.5 rounded-full font-bold">WINNER</span>
          )}
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500 font-sans">Route Option:</span>
            <span className="text-slate-800 font-semibold">{proposalB.recommended_route}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 font-sans">Ambulance ETA:</span>
            <span className="text-blue-600 font-bold">{proposalB.ambulance_eta} mins</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 font-sans">Vehicles Impacted:</span>
            <span className="text-slate-800">{proposalB.vehicles_impacted} vehicles</span>
          </div>
        </div>
      </article>
    </div>
  );
};
