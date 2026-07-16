import React from 'react';
import { useParams } from 'react-router-dom';
import { useIncidentStream } from '../hooks/useIncidentStream';

export interface StreamLog {
  timestamp: number;
  message: string;
}

interface AgentReasoningStreamProps {
  logs?: StreamLog[];
  status?: string;
}

export const AgentReasoningStream: React.FC<AgentReasoningStreamProps> = ({ logs: propLogs, status: propStatus }) => {
  const { id } = useParams<{ id: string }>();
  const stream = useIncidentStream(propLogs ? null : (id || null));

  const logs = propLogs !== undefined ? propLogs : stream.logs;
  const status = propStatus !== undefined ? propStatus : stream.status;
  return (
    <div className="w-full bg-slate-50 border border-slate-200 rounded-2xl p-5 flex flex-col gap-4 shadow-sm">
      <div className="flex justify-between items-center pb-3 border-b border-slate-200">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono">Pipeline Thought Stream</span>
        {status === 'processing' && <span className="animate-pulse text-blue-650 text-blue-600 text-[10px] font-bold">● LIVE</span>}
      </div>
      
      <div className="h-64 overflow-y-auto space-y-2.5 font-mono text-xs text-slate-700 select-text pr-2 scrollbar-thin">
        {logs.length === 0 ? (
          <div className="text-slate-450 italic">No incident active. Stream idle.</div>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className="flex gap-2 items-start leading-relaxed">
              <span className="text-slate-400">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
              <span>{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
