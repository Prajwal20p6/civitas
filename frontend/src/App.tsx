import React from 'react';
import { BrowserRouter, Routes, Route, Link, useParams, useLocation, Navigate } from 'react-router-dom';
import { Dashboard } from './components/Dashboard';
import { AgentReasoningStream } from './components/AgentReasoningStream';
import { ProposalComparison } from './components/ProposalComparison';
import { SimulationHeatmaps } from './components/SimulationHeatmaps';
import { ApprovalModal } from './components/ApprovalModal';
import { ExecutionAnimation } from './components/ExecutionAnimation';
import { useIncidentStream } from './hooks/useIncidentStream';

const IncidentLayout: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const { status } = useIncidentStream(id || null);

  if (!id) return <Navigate to="/" replace />;

  const isTabActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-white text-slate-800 p-6 flex flex-col gap-6 font-sans">
      {/* Success Banner */}
      {status === 'success' && (
        <div className="bg-blue-600 text-white p-4 rounded-2xl flex items-center justify-between animate-fade-in font-mono text-sm shadow-md">
          <div className="flex items-center gap-2">
            <span>🎉</span>
            <span><strong>Preemption Success:</strong> Ambulance has arrived safely at destination. Emergency green wave corridor cleared.</span>
          </div>
          <Link 
            to="/"
            onClick={() => {
              localStorage.removeItem(`civitas_demo_start_${id}`);
            }}
            className="px-3 py-1 bg-white hover:bg-slate-100 text-blue-600 rounded-lg transition text-xs font-semibold font-sans hover:scale-105"
          >
            New Scenario
          </Link>
        </div>
      )}

      {/* Top Banner Navigation */}
      <header className="flex justify-between items-center border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <span className="w-4 h-4 bg-blue-600 rounded-full animate-pulse shadow-[0_0_12px_rgba(25,118,210,0.6)]" />
          <Link to="/" className="text-xl font-bold tracking-wider uppercase text-slate-800 font-mono hover:text-blue-600 transition-colors">
            CIVITAS Traffic Coordinator
          </Link>
        </div>
        <div className="bg-slate-100 border border-slate-200 rounded-lg px-3 py-1 font-mono text-xs text-slate-600">
          Session: <span className="text-blue-600 font-bold">{id}</span>
        </div>
      </header>

      {/* Route Navigation Tabs */}
      <nav className="flex flex-wrap gap-2 border-b border-slate-200 pb-4">
        <Link 
          to="/"
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-xs font-semibold rounded-xl transition duration-200 border border-slate-200 text-slate-600"
        >
          🗺️ Dashboard
        </Link>
        <Link 
          to={`/incident/${id}`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}`) 
              ? 'bg-blue-600 text-white border-blue-600 shadow-[0_2px_8px_rgba(25,118,210,0.15)]' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200'
          }`}
        >
          🤖 Thought Stream
        </Link>
        <Link 
          to={`/incident/${id}/comparison`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/comparison`) 
              ? 'bg-blue-600 text-white border-blue-600 shadow-[0_2px_8px_rgba(25,118,210,0.15)]' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200'
          }`}
        >
          ⚖️ Comparisons
        </Link>
        <Link 
          to={`/incident/${id}/heatmaps`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/heatmaps`) 
              ? 'bg-blue-600 text-white border-blue-600 shadow-[0_2px_8px_rgba(25,118,210,0.15)]' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200'
          }`}
        >
          🔥 Heatmaps
        </Link>
        <Link 
          to={`/incident/${id}/approval`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/approval`) 
              ? 'bg-blue-600 text-white border-blue-600 shadow-[0_2px_8px_rgba(25,118,210,0.15)]' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200'
          }`}
        >
          ⚠️ Operator Approval
        </Link>
        <Link 
          to={`/incident/${id}/execution`}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition duration-200 border ${
            isTabActive(`/incident/${id}/execution`) 
              ? 'bg-blue-600 text-white border-blue-600 shadow-[0_2px_8px_rgba(25,118,210,0.15)]' 
              : 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200'
          }`}
        >
          ⚡ Preemption Active
        </Link>
      </nav>

      {/* Main Area Area */}
      <div className="flex-1 bg-white border border-slate-100 rounded-3xl p-6 shadow-md min-h-[400px]">
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
