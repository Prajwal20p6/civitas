import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useFirestore } from '../hooks/useFirestore';

interface ExecutionAnimationProps {
  status?: string;
  winner?: string | null;
}

export const ExecutionAnimation: React.FC<ExecutionAnimationProps> = ({ status: propStatus, winner: propWinner }) => {
  const { id } = useParams<{ id: string }>();
  const { incidentData } = useFirestore(propStatus !== undefined ? null : (id || null));

  const isActive = !!id || propStatus !== undefined;
  if (!isActive) return null;

  const status = propStatus !== undefined ? propStatus : incidentData?.status || (id ? 'executing' : 'idle');
  const winner = propWinner !== undefined ? propWinner : incidentData?.decision?.winner || (id ? 'route_a_speed_first' : null);

  const [progress, setProgress] = useState(0);
  const [countdown, setCountdown] = useState(15);

  useEffect(() => {
    if (status !== 'executing') {
      setProgress(0);
      setCountdown(15);
      return;
    }

    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          return 100;
        }
        return p + 10;
      });
      setCountdown((c) => (c > 0 ? c - 1.5 : 0));
    }, 400);

    return () => clearInterval(interval);
  }, [status]);

  if (status !== 'executing') return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-2xl animate-pulse">
      <div className="flex justify-between items-center">
        <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono">Emergency Corridor Active</span>
        <span className="text-xs font-mono text-slate-400">ETA Countdown: <strong className="text-white">{countdown.toFixed(1)}s</strong></span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
        <div 
          className="bg-emerald-500 h-full transition-all duration-300 shadow-[0_0_12px_#10b981]" 
          style={{ width: `${progress}%` }} 
        />
      </div>

      <div className="text-[11px] font-mono text-slate-400 space-y-1">
        <div>Preemption Route: <span className="text-white">{winner === 'route_a_speed_first' ? 'Surface Streets' : 'Highway 1'}</span></div>
        <div className="flex gap-2">
          <span>Signal status:</span>
          <span className="text-emerald-400">INT_01 [GREEN WAVE]</span>
          <span className="text-emerald-400">INT_02 [GREEN WAVE]</span>
          <span className="text-emerald-400">INT_03 [GREEN WAVE]</span>
        </div>
      </div>
    </div>
  );
};
