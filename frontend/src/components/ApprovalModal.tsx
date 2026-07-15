import React from 'react';

interface ApprovalModalProps {
  show: boolean;
  onApprove: () => void;
  onOverride: () => void;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({ show, onApprove, onOverride }) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-slate-900 border border-rose-500/40 rounded-3xl p-6 max-w-md w-full space-y-5 shadow-2xl shadow-rose-500/10">
        <div className="flex items-center gap-3 text-rose-500">
          <span className="text-2xl" role="img" aria-label="warning">⚠️</span>
          <h3 className="text-md font-bold uppercase tracking-wider font-mono">Operator Approval Required</h3>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed">
          The winning plan (Plan A: Surface Streets) impacts more than 10 vehicles. Please approve green wave preemption sequence.
        </p>
        <div className="flex gap-4">
          <button 
            onClick={onApprove}
            className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white text-xs font-bold uppercase tracking-widest rounded-xl transition-all duration-300 font-mono"
          >
            Approve Plan
          </button>
          <button 
            onClick={onOverride}
            className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-300 text-xs font-bold uppercase tracking-widest rounded-xl transition-all duration-300 font-mono"
          >
            Override
          </button>
        </div>
      </div>
    </div>
  );
};
