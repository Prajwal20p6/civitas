import React from 'react';
import { BrowserRouter, Routes, Route, Link, useParams, useLocation, Navigate } from 'react-router-dom';
import { Dashboard } from './components/Dashboard';
import { AgentReasoningStream } from './components/AgentReasoningStream';
import { ProposalComparison } from './components/ProposalComparison';
import { SimulationHeatmaps } from './components/SimulationHeatmaps';
import { ApprovalModal } from './components/ApprovalModal';
import { ExecutionAnimation } from './components/ExecutionAnimation';

const IncidentLayout: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();

  if (!id) return <Navigate to="/" replace />;

  const isTabActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 flex flex-col gap-6 font-sans">
      {/* Top Banner Navigation */}
      <header className="flex justify-between items-center border-b border-slate-900 pb-4">
        <div className="flex items-center gap-3">
          <span className="w-4 h-4 bg-rose-500 rounded-full animate-pulse shadow-[0_0_12px_rgba(244,63,94,0.6)]" />
          <Link to="/" className="text-xl font-bold tracking-wider uppercase text-white font-mono hover:text-rose-400 transition-colors">
            CIVITAS Traffic Coordinator
          </Link>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1 font-mono text-xs text-slate-400">
          Session: <span className="text-rose-400 font-bold">{id}</span>
        </div>
      </header>

      {/* Route Navigation Tabs */}
      <nav className="flex flex-wrap gap-2 border-b border-slate-900 pb-4">
        <Link 
          to="/"
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-xs font-semibold rounded-xl transition duration-200 border border-slate-805 text-slate-400"
        >
          🗺️ Dashboard
        </Link>
        <Link 
          to={`/incident/${id}`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}`) 
              ? 'bg-rose-605 text-white border-rose-500 bg-rose-600 shadow-[0_4px_12px_rgba(225,29,72,0.25)]' 
              : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800'
          }`}
        >
          🤖 Thought Stream
        </Link>
        <Link 
          to={`/incident/${id}/comparison`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/comparison`) 
              ? 'bg-rose-605 text-white border-rose-500 bg-rose-600 shadow-[0_4px_12px_rgba(225,29,72,0.25)]' 
              : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800'
          }`}
        >
          ⚖️ Comparisons
        </Link>
        <Link 
          to={`/incident/${id}/heatmaps`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/heatmaps`) 
              ? 'bg-rose-650 text-white border-rose-500 bg-rose-600 shadow-[0_4px_12px_rgba(225,29,72,0.25)]' 
              : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800'
          }`}
        >
          🔥 Heatmaps
        </Link>
        <Link 
          to={`/incident/${id}/approval`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/approval`) 
              ? 'bg-rose-650 text-white border-rose-500 bg-rose-600 shadow-[0_4px_12px_rgba(225,29,72,0.25)]' 
              : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800'
          }`}
        >
          ⚠️ Operator Approval
        </Link>
        <Link 
          to={`/incident/${id}/execution`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/execution`) 
              ? 'bg-rose-650 text-white border-rose-500 bg-rose-600 shadow-[0_4px_12px_rgba(225,29,72,0.25)]' 
              : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800'
          }`}
        >
          ⚡ Preemption Active
        </Link>
      </nav>

      {/* Main Area Area */}
      <div className="flex-1 bg-slate-900/40 border border-slate-900 rounded-3xl p-6 shadow-2xl min-h-[400px]">
        <Routes>
          <Route path="/" element={<AgentReasoningStream />} />
          <Route path="comparison" element={<ProposalComparison />} />
          <Route path="heatmaps" element={<SimulationHeatmaps />} />
          <Route path="approval" element={<ApprovalModal show={true} />} />
          <Route path="execution" element={<ExecutionAnimation />} />
        </Routes>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/incident/:id/*" element={<IncidentLayout />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
