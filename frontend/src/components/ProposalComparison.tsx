import React from 'react';

export interface RouteProposal {
  recommended_route: string;
  ambulance_eta: number;
  vehicles_impacted: number;
  avg_delay_per_vehicle?: number;
  safety_score?: number;
  reasoning?: string;
}

interface ProposalComparisonProps {
  proposalA: RouteProposal | null;
  proposalB: RouteProposal | null;
  winner: string | null;
}

export const ProposalComparison: React.FC<ProposalComparisonProps> = ({ proposalA, proposalB, winner }) => {
  if (!proposalA || !proposalB) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Proposal A: Speed-First */}
      <article className={`p-5 rounded-2xl border transition-all duration-300 ${
        winner === 'route_a_speed_first' 
          ? 'bg-slate-900/60 border-emerald-500/50 shadow-lg shadow-emerald-500/5' 
          : 'bg-slate-900/20 border-slate-850 opacity-40'
      }`}>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Plan A (Speed-First)</h3>
          {winner === 'route_a_speed_first' && (
            <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-0.5 rounded-full font-bold">WINNER</span>
          )}
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500">Route Option:</span>
            <span className="text-white font-medium">{proposalA.recommended_route}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Ambulance ETA:</span>
            <span className="text-emerald-400 font-bold">{proposalA.ambulance_eta} mins</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Vehicles Impacted:</span>
            <span className="text-white">{proposalA.vehicles_impacted} vehicles</span>
          </div>
        </div>
      </article>

      {/* Proposal B: Fairness-First */}
      <article className={`p-5 rounded-2xl border transition-all duration-300 ${
        winner === 'route_b_fairness_first' 
          ? 'bg-slate-900/60 border-emerald-500/50 shadow-lg shadow-emerald-500/5' 
          : 'bg-slate-900/20 border-slate-850 opacity-40'
      }`}>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Plan B (Fairness-First)</h3>
          {winner === 'route_b_fairness_first' && (
            <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-0.5 rounded-full font-bold">WINNER</span>
          )}
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500">Route Option:</span>
            <span className="text-white font-medium">{proposalB.recommended_route}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Ambulance ETA:</span>
            <span className="text-emerald-400 font-bold">{proposalB.ambulance_eta} mins</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Vehicles Impacted:</span>
            <span className="text-white">{proposalB.vehicles_impacted} vehicles</span>
          </div>
        </div>
      </article>
    </div>
  );
};
