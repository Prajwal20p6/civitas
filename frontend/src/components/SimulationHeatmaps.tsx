import React from 'react';
import { useParams } from 'react-router-dom';
import { useFirestore } from '../hooks/useFirestore';

interface SimulationHeatmapsProps {
  scoreA?: number | null;
  scoreB?: number | null;
}

export const SimulationHeatmaps: React.FC<SimulationHeatmapsProps> = ({ scoreA: propScoreA, scoreB: propScoreB }) => {
  const { id } = useParams<{ id: string }>();
  const { incidentData } = useFirestore(propScoreA !== undefined && propScoreA !== null ? null : (id || null));

  const isActive = !!id || (propScoreA !== undefined && propScoreA !== null);
  if (!isActive) return null;

  const scoreA = propScoreA !== undefined && propScoreA !== null ? propScoreA : incidentData?.negotiation_result?.score_a || (id ? 92 : null);
  const scoreB = propScoreB !== undefined && propScoreB !== null ? propScoreB : incidentData?.negotiation_result?.score_b || (id ? 74 : null);

  if (scoreA === null || scoreB === null) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-2xl">
      <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Simulation Congestion Heatmaps</h3>
      <div className="grid grid-cols-2 gap-4">
        {/* Heatmap A */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex flex-col items-center gap-3">
          <span className="text-[10px] font-mono text-slate-500">SCENARIO A (SURFACE STREETS)</span>
          <div className="w-full h-24 bg-gradient-to-br from-rose-950/40 via-red-950/20 to-slate-950 rounded-lg border border-red-500/20 flex flex-wrap gap-1 p-2 items-center justify-center">
            {/* Grid of nodes */}
            {Array.from({ length: 15 }).map((_, i) => (
              <span 
                key={i} 
                className={`w-3.5 h-3.5 rounded-sm ${
                  i % 3 === 0 ? 'bg-red-500 animate-pulse shadow-[0_0_8px_#ef4444]' : 'bg-slate-800'
                }`} 
              />
            ))}
          </div>
          <span className="text-xs font-mono text-rose-400 font-bold">Congestion Score: {scoreA}</span>
        </div>

        {/* Heatmap B */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex flex-col items-center gap-3">
          <span className="text-[10px] font-mono text-slate-500">SCENARIO B (HIGHWAY 1)</span>
          <div className="w-full h-24 bg-gradient-to-br from-emerald-950/40 via-slate-950 to-slate-950 rounded-lg border border-emerald-500/20 flex flex-wrap gap-1 p-2 items-center justify-center">
            {/* Grid of nodes */}
            {Array.from({ length: 15 }).map((_, i) => (
              <span 
                key={i} 
                className={`w-3.5 h-3.5 rounded-sm ${
                  i % 5 === 0 ? 'bg-emerald-500 shadow-[0_0_6px_#10b981]' : 'bg-slate-850'
                }`} 
              />
            ))}
          </div>
          <span className="text-xs font-mono text-emerald-400 font-bold">Congestion Score: {scoreB}</span>
        </div>
      </div>
    </div>
  );
};
