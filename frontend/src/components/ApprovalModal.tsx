import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFirestore } from '../hooks/useFirestore';
import { api } from '../api/client';

interface ApprovalModalProps {
  show?: boolean;
  onApprove?: () => void;
  onOverride?: () => void;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({ 
  show: propShow, 
  onApprove: propOnApprove, 
  onOverride: propOnOverride 
}) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { incidentData } = useFirestore(propShow !== undefined ? null : (id || null));

  // Show if propShow is true, or if we have an ID and status is pending_approval, or if we are on approval route.
  const show = propShow !== undefined ? propShow : (!!id && (incidentData?.status === 'pending_approval' || true));

  if (!show) return null;

  const handleAction = async (approved: boolean) => {
    if (propOnApprove && approved) {
      propOnApprove();
      return;
    }
    if (propOnOverride && !approved) {
      propOnOverride();
      return;
    }

    if (id) {
      try {
        await api.approveIncident(id, approved ? 'approved' : 'denied', "Operator cleared green waves.");
        if (approved) {
          navigate(`/incident/${id}/execution`);
        } else {
          navigate(`/`);
        }
      } catch (err) {
        console.error("Failed to post approval state", err);
        navigate(`/`);
      }
    } else {
      navigate(`/`);
    }
  };

  const onApprove = () => handleAction(true);
  const onOverride = () => handleAction(false);

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
