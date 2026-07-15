import React from 'react';

export interface StreamLog {
  timestamp: number;
  message: string;
}

interface AgentReasoningStreamProps {
  logs: StreamLog[];
  status: string;
}

export const AgentReasoningStream: React.FC<AgentReasoningStreamProps> = ({ logs, status }) => {
  return (
    <div className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col gap-4 shadow-2xl">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Pipeline Thought Stream</span>
        {status === 'processing' && <span className="animate-pulse text-rose-500 text-[10px] font-bold">● LIVE</span>}
      </div>
      
      <div className="h-64 overflow-y-auto space-y-2.5 font-mono text-xs text-emerald-400 select-text pr-2 scrollbar-thin scrollbar-thumb-slate-800">
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
  );
};
