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
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
      <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono">Simulation Congestion Heatmaps</h3>
      <div className="grid grid-cols-2 gap-4">
        {/* Heatmap A */}
        <div className="bg-white border border-slate-250 border-slate-200 rounded-xl p-3 flex flex-col items-center gap-3 shadow-sm">
          <span className="text-[10px] font-mono text-slate-500">SCENARIO A (SURFACE STREETS)</span>
          <div className="w-full h-24 bg-slate-50 rounded-lg border border-slate-200 flex flex-wrap gap-1 p-2 items-center justify-center">
            {/* Grid of nodes */}
            {Array.from({ length: 15 }).map((_, i) => (
              <span 
                key={i} 
                className={`w-3.5 h-3.5 rounded-sm ${
                  i % 3 === 0 ? 'bg-red-500' : 'bg-slate-200'
                }`} 
              />
            ))}
          </div>
          <span className="text-xs font-mono text-red-600 font-bold">Congestion Score: {scoreA}</span>
        </div>

        {/* Heatmap B */}
        <div className="bg-white border border-slate-250 border-slate-200 rounded-xl p-3 flex flex-col items-center gap-3 shadow-sm">
          <span className="text-[10px] font-mono text-slate-500">SCENARIO B (HIGHWAY 1)</span>
          <div className="w-full h-24 bg-slate-50 rounded-lg border border-slate-200 flex flex-wrap gap-1 p-2 items-center justify-center">
            {/* Grid of nodes */}
            {Array.from({ length: 15 }).map((_, i) => (
              <span 
                key={i} 
                className={`w-3.5 h-3.5 rounded-sm ${
                  i % 5 === 0 ? 'bg-emerald-500' : 'bg-slate-200'
                }`} 
              />
            ))}
          </div>
          <span className="text-xs font-mono text-emerald-605 text-emerald-600 font-bold">Congestion Score: {scoreB}</span>
        </div>
      </div>
    </div>
  );
};
