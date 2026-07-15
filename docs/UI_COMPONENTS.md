# CIVITAS — Dashboard Screen Designs & UI Components

This document outlines the six core screen experiences displayed on the CIVITAS Dashboard and includes React/Tailwind code snippets for implementation.

---

## 1. Core Screen Experiences

### Screen 1: Dashboard (Landing State)
- **Visuals**: A full-screen dark-theme map showing current traffic flow (green/yellow/red). A right sidebar contains the incident log feeds and a prominent red `Trigger Emergency Scenario` button.
- **Goal**: Establish a baseline overview of city traffic before an incident is generated.

### Screen 2: Live Agent Stream
- **Visuals**: Triggered immediately upon clicking the emergency scenario button. The right sidebar expands into a retro-style terminal output printing log lines with emoji indicators as agents execute.
- **Goal**: Demystify agent execution, showing the sequential reasoning steps.

### Screen 3: Proposal Comparison View
- **Visuals**: A side-by-side card comparison layout of the speed-first vs. fairness-first proposals. The winning option is outlined in high-contrast blue, and the losing option is semi-transparent.
- **Goal**: Clearly highlight the policy trade-offs (ETA vs. grid congestion impact).

### Screen 4: Simulation Heatmaps
- **Visuals**: Display grid visualizations of the road network for both plans, highlighting congested intersections as red heat signatures.
- **Goal**: Graphically prove the correctness of the Simulation Agent's deterministic scoring.

### Screen 5: Approval Modal Screen
- **Visuals**: A high-impact operator modal overlay showing a warning header: `⚠️ HIGH-IMPACT DECISION — REQUIRES APPROVAL` alongside `APPROVE` and `OVERRIDE` actions.
- **Goal**: Highlight safety and operator control over agent decisions.

### Screen 6: Execution & Results
- **Visuals**: An active map animation showing the ambulance moving along the chosen corridor, with traffic lights transitioning to green in sequence (Green Wave preemption). Live countdown timer shown at top-right.
- **Goal**: Deliver a satisfying visual climax showing successful emergency response.

---

## 2. React + Tailwind CSS Components

### Component: Agent Thought Stream Terminal
```typescript
import React from 'react';

interface EventLog {
  timestamp: number;
  agent: string;
  emoji: string;
  message: string;
}

export const AgentStreamTerminal: React.FC<{ events: EventLog[] }> = ({ events }) => {
  return (
    <div className="w-full bg-gray-950 border border-gray-800 rounded-lg p-4 font-mono text-xs text-green-400 max-h-80 overflow-y-auto shadow-2xl">
      <div className="flex items-center justify-between pb-2 border-b border-gray-800 mb-3 text-gray-500">
        <span>AGENT REASONING PIPELINE</span>
        <span className="animate-pulse text-red-500">● LIVE</span>
      </div>
      <div className="space-y-2">
        {events.map((evt, idx) => (
          <div key={idx} className="flex items-start gap-2">
            <span className="text-gray-600">[{evt.timestamp.toFixed(1)}s]</span>
            <span className="text-blue-400 font-bold">{evt.agent}:</span>
            <span>{evt.emoji} {evt.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Component: Proposal Comparison Cards
```typescript
import React from 'react';

interface RouteProposal {
  route: string;
  eta: number;
  vehicles_impacted: number;
  avg_delay: number;
  score: number;
}

export const ProposalComparison: React.FC<{
  proposalA: RouteProposal;
  proposalB: RouteProposal;
  winner: 'a' | 'b';
}> = ({ proposalA, proposalB, winner }) => {
  return (
    <div className="grid grid-cols-2 gap-4 my-6">
      {/* Route A (Speed-First) */}
      <div className={`p-5 rounded-xl border transition-all ${
        winner === 'a' 
          ? 'bg-blue-950/30 border-blue-500 shadow-lg shadow-blue-500/10' 
          : 'bg-gray-900/40 border-gray-800 opacity-60'
      }`}>
        <div className="flex justify-between items-start mb-4">
          <h4 className="text-sm font-semibold text-blue-400 uppercase tracking-wider">Plan A: Speed-First</h4>
          {winner === 'a' && <span className="bg-blue-500 text-black text-2xs px-2 py-0.5 rounded-full font-bold">WINNER</span>}
        </div>
        <div className="space-y-3 text-sm text-gray-300">
          <div className="flex justify-between"><span>Route:</span><span className="font-medium text-white">{proposalA.route}</span></div>
          <div className="flex justify-between"><span>Ambulance ETA:</span><span className="text-green-400 font-bold">{proposalA.eta} mins</span></div>
          <div className="flex justify-between"><span>Non-emergency Delayed:</span><span>{proposalA.vehicles_impacted} vehicles</span></div>
          <div className="flex justify-between"><span>Avg Delay Time:</span><span>{proposalA.avg_delay} mins</span></div>
          <div className="border-t border-gray-800 pt-3 flex justify-between items-center">
            <span className="text-gray-500">Evaluation Score:</span>
            <span className="text-lg font-bold text-white">{proposalA.score}/100</span>
          </div>
        </div>
      </div>

      {/* Route B (Fairness-First) */}
      <div className={`p-5 rounded-xl border transition-all ${
        winner === 'b' 
          ? 'bg-orange-950/30 border-orange-500 shadow-lg shadow-orange-500/10' 
          : 'bg-gray-900/40 border-gray-800 opacity-60'
      }`}>
        <div className="flex justify-between items-start mb-4">
          <h4 className="text-sm font-semibold text-orange-400 uppercase tracking-wider">Plan B: Fairness-First</h4>
          {winner === 'b' && <span className="bg-orange-500 text-black text-2xs px-2 py-0.5 rounded-full font-bold">WINNER</span>}
        </div>
        <div className="space-y-3 text-sm text-gray-300">
          <div className="flex justify-between"><span>Route:</span><span className="font-medium text-white">{proposalB.route}</span></div>
          <div className="flex justify-between"><span>Ambulance ETA:</span><span className="text-green-400 font-bold">{proposalB.eta} mins</span></div>
          <div className="flex justify-between"><span>Non-emergency Delayed:</span><span>{proposalB.vehicles_impacted} vehicles</span></div>
          <div className="flex justify-between"><span>Avg Delay Time:</span><span>{proposalB.avg_delay} mins</span></div>
          <div className="border-t border-gray-800 pt-3 flex justify-between items-center">
            <span className="text-gray-500">Evaluation Score:</span>
            <span className="text-lg font-bold text-white">{proposalB.score}/100</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```
