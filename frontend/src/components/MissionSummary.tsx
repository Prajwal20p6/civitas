import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useFirestore } from '../hooks/useFirestore';

interface MissionSummaryProps {
  incidentId: string | null;
  winner?: string | null;
  onReset?: () => void;
}

export const MissionSummary: React.FC<MissionSummaryProps> = ({ incidentId, winner: propWinner, onReset }) => {
  const navigate = useNavigate();
  const { incidentData } = useFirestore(incidentId);

  // Fallback resolving details based on incidentId if offline/demo
  let data = incidentData;
  if (!data && incidentId) {
    if (incidentId.includes('_hazard')) {
      data = {
        incident_type: 'hazard',
        perception: { incident_type: 'hazard', severity: 'minor', priority_score: 0.4 },
        route_a_proposal: { recommended_route: 'Surface Streets', ambulance_eta: 15, vehicles_impacted: 10, avg_delay_per_vehicle: 2, safety_score: 0.85 },
        route_b_proposal: { recommended_route: 'Highway 1', ambulance_eta: 16, vehicles_impacted: 2, avg_delay_per_vehicle: 4, safety_score: 0.87 },
        decision: { winner: 'route_b_fairness_first' },
        negotiation_result: { winner: 'route_b_fairness_first', score_a: 85, score_b: 87, counterfactual: { baseline_eta_no_intervention: 25, planned_eta_with_intervention: 16, time_saved: 9 } },
        explainability: { reasoning_one_liner: 'Highway 1 route recommended. Saves 9 minutes with negligible collateral delay (2 vehicles). Auto-executing.' }
      };
    } else if (incidentId.includes('_accident')) {
      data = {
        incident_type: 'accident',
        perception: { incident_type: 'accident', severity: 'major', priority_score: 0.7 },
        route_a_proposal: { recommended_route: 'Surface Streets', ambulance_eta: 9, vehicles_impacted: 18, avg_delay_per_vehicle: 3, safety_score: 0.88 },
        route_b_proposal: { recommended_route: 'Highway 1', ambulance_eta: 12, vehicles_impacted: 6, avg_delay_per_vehicle: 5, safety_score: 0.82 },
        decision: { winner: 'route_a_speed_first' },
        negotiation_result: { winner: 'route_a_speed_first', score_a: 88, score_b: 82, counterfactual: { baseline_eta_no_intervention: 18, planned_eta_with_intervention: 9, time_saved: 9 } },
        explainability: { reasoning_one_liner: 'Plan A chosen with close margin (88 vs 82). Saves 9 minutes but delays 18 vehicles by 3 minutes. Standard approval required.' }
      };
    } else {
      data = {
        incident_type: 'medical_emergency',
        perception: { incident_type: 'medical_emergency', severity: 'critical', priority_score: 0.95 },
        route_a_proposal: { recommended_route: 'Surface Streets', ambulance_eta: 7, vehicles_impacted: 14, avg_delay_per_vehicle: 2, safety_score: 0.92 },
        route_b_proposal: { recommended_route: 'Highway 1', ambulance_eta: 10, vehicles_impacted: 5, avg_delay_per_vehicle: 4, safety_score: 0.85 },
        decision: { winner: 'route_a_speed_first' },
        negotiation_result: { winner: 'route_a_speed_first', score_a: 93, score_b: 75, counterfactual: { baseline_eta_no_intervention: 22, planned_eta_with_intervention: 7, time_saved: 15 } },
        explainability: { reasoning_one_liner: 'Surface Streets saves ambulance 15 minutes, delaying 14 vehicles for 2 minutes average. Critical emergency warrants prioritizing speed.' }
      };
    }
  }

  if (!data) return null;

  const typeLabel = data.perception?.incident_type?.replace('_', ' ').toUpperCase() || 'EMERGENCY';
  const severity = data.perception?.severity || 'critical';
  const winner = propWinner || data.decision?.winner || data.negotiation_result?.winner || 'route_a_speed_first';
  const winnerRoute = winner === 'route_a_speed_first' ? 'Surface Streets' : 'Highway 1';
  const counterfactual = data.negotiation_result?.counterfactual || { baseline_eta_no_intervention: 22, planned_eta_with_intervention: 8, time_saved: 14 };
  const routeA = data.route_a_proposal || { recommended_route: 'Surface Streets', ambulance_eta: 8, vehicles_impacted: 12, safety_score: 0.9 };
  const routeB = data.route_b_proposal || { recommended_route: 'Highway 1', ambulance_eta: 11, vehicles_impacted: 3, safety_score: 0.8 };
  const explainText = data.explainability?.reasoning_one_liner || 'Decision completed and optimized.';

  const handleReset = () => {
    if (onReset) {
      onReset();
    } else {
      localStorage.clear();
      navigate('/');
      window.location.reload();
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-lg space-y-6 md:space-y-8 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col items-center text-center space-y-3 pb-6 border-b border-slate-100">
        <div className="bg-emerald-100 text-emerald-600 w-16 h-16 rounded-full flex items-center justify-center text-3xl shadow-sm border border-emerald-200">
          ✓
        </div>
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">Preemption Corridor Completed</h2>
          <p className="text-sm font-mono text-slate-400 mt-1">Incident ID: {incidentId}</p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
        
        {/* Card 1: Mission Brief */}
        <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Mission Brief</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Patient Type:</span>
              <span className="font-semibold text-slate-800">{typeLabel}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Severity Classification:</span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${
                severity === 'critical' ? 'bg-rose-100 text-rose-700' : 
                (severity === 'major' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700')
              }`}>
                {severity}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Preemption Route:</span>
              <span className="font-semibold text-blue-600">{winnerRoute}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Approval Execution:</span>
              <span className="font-semibold text-slate-700">
                {data.perception?.priority_score >= 0.4 ? 'Operator Approved' : 'Auto-Executed (Low Risk)'}
              </span>
            </div>
          </div>
        </div>

        {/* Card 2: Outcome Metrics */}
        <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Performance Impact</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Baseline Hospital ETA:</span>
              <span className="font-semibold text-slate-500 line-through font-mono">{counterfactual.baseline_eta_no_intervention} mins</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Preemption Hospital ETA:</span>
              <span className="font-bold text-emerald-600 font-mono">{counterfactual.planned_eta_with_intervention} mins</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Total Time Saved:</span>
              <span className="bg-emerald-100 text-emerald-700 font-bold px-2 py-0.5 rounded-full text-xs font-mono">
                -{counterfactual.time_saved} mins saved
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Civilians Impacted:</span>
              <span className="font-semibold text-slate-800 font-mono">
                {winner === 'route_a_speed_first' ? routeA.vehicles_impacted : routeB.vehicles_impacted} vehicles delayed
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Card 3: Decision Explanation */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">System Decision Brief</h3>
        <p className="text-sm font-medium text-slate-700 leading-relaxed italic">
          "{explainText}"
        </p>
      </div>

      {/* Decision Scorecard */}
      <div className="border border-slate-100 rounded-2xl p-5 space-y-4 bg-slate-50/50">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">Multi-Agent Negotiation Margin</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className={`p-4 rounded-xl border ${winner === 'route_a_speed_first' ? 'bg-blue-50/40 border-blue-200' : 'bg-slate-50 border-slate-200'}`}>
            <div className="text-xs text-slate-400 font-mono">AGENT A (Speed Priority)</div>
            <div className="text-lg font-bold text-slate-800 mt-1">{winner === 'route_a_speed_first' ? `${data.negotiation_result?.score_a || 92} / 100` : `${data.negotiation_result?.score_a || 85} / 100`}</div>
            <div className="text-[11px] text-slate-500 mt-2">Recommended: {routeA.recommended_route}</div>
            <div className="text-[11px] text-slate-500">ETA: {routeA.ambulance_eta}m | Delays: {routeA.vehicles_impacted} cars</div>
          </div>
          
          <div className={`p-4 rounded-xl border ${winner === 'route_b_fairness_first' ? 'bg-blue-50/40 border-blue-200' : 'bg-slate-50 border-slate-200'}`}>
            <div className="text-xs text-slate-400 font-mono">AGENT B (Fairness Priority)</div>
            <div className="text-lg font-bold text-slate-800 mt-1">{winner === 'route_b_fairness_first' ? `${data.negotiation_result?.score_b || 87} / 100` : `${data.negotiation_result?.score_b || 74} / 100`}</div>
            <div className="text-[11px] text-slate-500 mt-2">Recommended: {routeB.recommended_route}</div>
            <div className="text-[11px] text-slate-500">ETA: {routeB.ambulance_eta}m | Delays: {routeB.vehicles_impacted} cars</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center pt-4">
        <button
          onClick={handleReset}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-full shadow-md hover:shadow-lg transition duration-200 text-sm font-mono uppercase tracking-wider"
        >
          Start New Scenario
        </button>
      </div>
    </div>
  );
};
