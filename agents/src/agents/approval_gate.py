"""
ADK Human Approval Gate — workflow pause node.

This agent implements a human-in-the-loop approval gate within the CIVITAS
orchestration pipeline. When invoked, it:

1. Updates the incident status to 'pending_approval' in Firestore
2. Pushes reasoning logs explaining why approval is required
3. Polls Firestore at regular intervals for the operator's decision
4. Returns the approval status once the operator acts (or auto-approves for low-impact)

For demo mode (CIVITAS_DEMO_MODE=true), the gate auto-approves after a
configurable delay to keep the demo flow running without manual intervention.
"""
import os
import time
import asyncio
import logging
from typing import Optional

from src.adk_setup import Agent
from src.schemas import ApprovalGateInput

logger = logging.getLogger(__name__)

# How often to poll Firestore for operator decision (seconds)
POLL_INTERVAL_SECONDS = 2.0

# Maximum time to wait before auto-timeout (seconds)
APPROVAL_TIMEOUT_SECONDS = 120.0

# Auto-approval threshold: incidents with impact_score below this
# are automatically approved without operator intervention
AUTO_APPROVE_THRESHOLD = 0.5

# Demo mode auto-approve delay
DEMO_AUTO_APPROVE_DELAY = 5.0


class ApprovalGateAgent(Agent):
    """
    Human-in-the-loop approval gate for the CIVITAS orchestration pipeline.

    Pauses the workflow and waits for an operator decision from Firestore.
    Supports auto-approval for low-impact incidents and demo mode bypass.
    """

    def __init__(self, db_client=None):
        super().__init__()
        self.db = db_client
        if self.db is None:
            self._init_db_client()

    def _init_db_client(self):
        """Lazily initialize the Firebase client."""
        try:
            import sys

            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            sys.path.append(base_dir)
            from backend.firebase_client import FirebaseClient

            self.db = FirebaseClient()
        except ImportError:
            logger.warning(
                "FirebaseClient not available; approval gate will use mock responses"
            )
            self.db = None

    async def execute(
        self, gate_input: ApprovalGateInput, incident_id: Optional[str] = None
    ) -> dict:
        """
        Execute the approval gate workflow.

        Args:
            gate_input: Approval gate parameters (incident_id, decision, reasoning, impact_score)
            incident_id: Override incident ID (if not specified in gate_input)

        Returns:
            dict with keys:
                - status: 'approved' | 'denied' | 'timeout' | 'auto_approved'
                - reason: str explaining the outcome
                - wait_time_seconds: float total wait time
        """
        i_id = incident_id or gate_input.incident_id
        impact = gate_input.impact_score

        logger.info(
            f"[ApprovalGate] Evaluating incident {i_id} (impact_score={impact:.2f})"
        )

        # 1. Check for auto-approval (low-impact incidents)
        if impact < AUTO_APPROVE_THRESHOLD:
            logger.info(
                f"[ApprovalGate] Auto-approving: impact_score {impact:.2f} below threshold {AUTO_APPROVE_THRESHOLD}"
            )
            if self.db:
                self.db.update_incident(i_id, {"status": "executing"})
                self.db.push_reasoning_log(
                    i_id,
                    f"[ApprovalGate] Auto-approved: impact below threshold ({impact:.2f} < {AUTO_APPROVE_THRESHOLD})",
                )
            return {
                "status": "auto_approved",
                "reason": f"Impact score {impact:.2f} below auto-approval threshold {AUTO_APPROVE_THRESHOLD}",
                "wait_time_seconds": 0.0,
            }

        # 2. Check demo mode
        demo_mode = os.environ.get("CIVITAS_DEMO_MODE", "").lower() == "true"
        if demo_mode:
            logger.info(
                f"[ApprovalGate] Demo mode: auto-approving after {DEMO_AUTO_APPROVE_DELAY}s delay"
            )
            if self.db:
                self.db.update_incident(i_id, {"status": "pending_approval"})
                self.db.push_reasoning_log(
                    i_id, "[ApprovalGate] Awaiting operator approval (demo mode)..."
                )

            await asyncio.sleep(DEMO_AUTO_APPROVE_DELAY)

            if self.db:
                self.db.update_incident(i_id, {"status": "executing"})
                self.db.push_reasoning_log(
                    i_id, "[ApprovalGate] Demo auto-approved. Proceeding to execution."
                )
            return {
                "status": "approved",
                "reason": "Demo mode auto-approval after delay",
                "wait_time_seconds": DEMO_AUTO_APPROVE_DELAY,
            }

        # 3. Real approval flow — update status and poll Firestore
        if self.db:
            self.db.update_incident(i_id, {"status": "pending_approval"})
            self.db.push_reasoning_log(
                i_id,
                f"[ApprovalGate] High-impact scenario ({impact:.2f}). Awaiting operator approval...",
            )

        t0 = time.monotonic()
        elapsed = 0.0

        while elapsed < APPROVAL_TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed = time.monotonic() - t0

            # Poll Firestore for operator decision
            if self.db:
                incident = self.db.get_incident(i_id)
                if incident:
                    operator_decision = incident.get("operator_decision", {})
                    current_status = incident.get("status", "pending_approval")

                    if current_status in ("executing", "denied"):
                        op_status = operator_decision.get("status", current_status)
                        op_reason = operator_decision.get(
                            "reason", "Operator decision recorded"
                        )

                        logger.info(
                            f"[ApprovalGate] Operator decision received: {op_status} ({elapsed:.1f}s)"
                        )
                        self.db.push_reasoning_log(
                            i_id,
                            f"[ApprovalGate] Operator {op_status}. Wait time: {elapsed:.1f}s. Reason: {op_reason}",
                        )
                        return {
                            "status": "approved"
                            if current_status == "executing"
                            else "denied",
                            "reason": op_reason,
                            "wait_time_seconds": elapsed,
                        }

            logger.debug(
                f"[ApprovalGate] Still waiting for approval... ({elapsed:.1f}s elapsed)"
            )

        # 4. Timeout — no operator response
        logger.warning(
            f"[ApprovalGate] Timeout after {APPROVAL_TIMEOUT_SECONDS}s. No operator response."
        )
        if self.db:
            self.db.update_incident(i_id, {"status": "timeout"})
            self.db.push_reasoning_log(
                i_id,
                f"[ApprovalGate] TIMEOUT: No operator response after {APPROVAL_TIMEOUT_SECONDS}s",
            )

        return {
            "status": "timeout",
            "reason": f"No operator response within {APPROVAL_TIMEOUT_SECONDS}s",
            "wait_time_seconds": elapsed,
        }
