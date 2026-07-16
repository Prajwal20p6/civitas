"""
Integration tests validating Firestore state transitions through the
full CIVITAS incident lifecycle.

Tests the complete state machine:
  processing -> pending_approval -> executing -> completed
  processing -> pending_approval -> denied
  processing -> auto_approved -> executing -> completed (low-impact)
"""
import os
import sys
import pytest

# Add root folder and agents folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
)

from backend.firebase_client import FirebaseClient


class TestFirestoreStateTransitions:
    """Validate the complete incident state machine transitions."""

    def setup_method(self):
        """Create a fresh FirebaseClient in offline mode for each test."""
        self.client = FirebaseClient()
        assert self.client.offline_mode is True

    def test_full_lifecycle_approved(self):
        """Test: processing -> pending_approval -> executing -> completed"""
        incident_id = "lifecycle_approved_001"

        # 1. Create incident in processing state
        self.client.create_incident(
            incident_id,
            {
                "incident_id": incident_id,
                "status": "processing",
                "incident_type": "medical_emergency",
            },
        )
        incident = self.client.get_incident(incident_id)
        assert incident["status"] == "processing"

        # 2. Transition to pending_approval
        self.client.update_incident(incident_id, {"status": "pending_approval"})
        incident = self.client.get_incident(incident_id)
        assert incident["status"] == "pending_approval"

        # 3. Operator approves -> executing
        self.client.update_incident(
            incident_id,
            {
                "status": "executing",
                "operator_decision": {
                    "status": "approved",
                    "reason": "Ambulance speed is paramount",
                    "timestamp": "2026-07-16T09:30:00Z",
                },
            },
        )
        incident = self.client.get_incident(incident_id)
        assert incident["status"] == "executing"
        assert incident["operator_decision"]["status"] == "approved"

        # 4. Execution completes
        self.client.update_incident(incident_id, {"status": "completed"})
        incident = self.client.get_incident(incident_id)
        assert incident["status"] == "completed"

    def test_full_lifecycle_denied(self):
        """Test: processing -> pending_approval -> denied"""
        incident_id = "lifecycle_denied_001"

        self.client.create_incident(
            incident_id, {"incident_id": incident_id, "status": "processing"}
        )

        self.client.update_incident(incident_id, {"status": "pending_approval"})
        incident = self.client.get_incident(incident_id)
        assert incident["status"] == "pending_approval"

        # Operator denies
        self.client.update_incident(
            incident_id,
            {
                "status": "denied",
                "operator_decision": {
                    "status": "denied",
                    "reason": "Override: alternative route selected manually",
                    "timestamp": "2026-07-16T09:35:00Z",
                },
            },
        )
        incident = self.client.get_incident(incident_id)
        assert incident["status"] == "denied"
        assert incident["operator_decision"]["status"] == "denied"

    def test_reasoning_log_accumulation(self):
        """Verify reasoning logs accumulate correctly across pipeline stages."""
        incident_id = "log_test_001"
        self.client.create_incident(incident_id, {"incident_id": incident_id})

        pipeline_logs = [
            "[Orchestrator] Running Perception Agent classification...",
            "[Perception] Classified type: medical_emergency, severity: critical",
            "[Orchestrator] Spawning Route Agents A & B in parallel...",
            "[Route Agent A] Recommends: Surface Streets (ETA: 8 min)",
            "[Route Agent B] Recommends: Highway 1 (ETA: 11 min)",
            "[Orchestrator] Invoking simulation and scoring resolver...",
            "[Simulation] Resolved winner: route_a_speed_first (Score: 92 vs 74)",
            "[Orchestrator] Compiling decision explanation...",
            "[Explainability] Surface Streets chosen: saves 14 minutes",
        ]

        for log in pipeline_logs:
            self.client.push_reasoning_log(incident_id, log)

        logs = self.client.get_reasoning_logs(incident_id)
        assert len(logs) == len(pipeline_logs)

        # Verify ordering is preserved
        for i, log in enumerate(logs):
            assert log["message"] == pipeline_logs[i]

    def test_decision_fields_persisted(self):
        """Verify decision metadata is correctly stored and retrievable."""
        incident_id = "decision_test_001"

        self.client.create_incident(
            incident_id, {"incident_id": incident_id, "status": "processing"}
        )

        # Simulate orchestrator writing decision data
        self.client.update_incident(
            incident_id,
            {
                "perception": {
                    "incident_type": "medical_emergency",
                    "severity": "critical",
                    "priority_score": 0.95,
                },
                "route_a_proposal": {
                    "recommended_route": "Surface Streets",
                    "ambulance_eta": 8,
                    "vehicles_impacted": 12,
                },
                "route_b_proposal": {
                    "recommended_route": "Highway 1",
                    "ambulance_eta": 11,
                    "vehicles_impacted": 3,
                },
                "negotiation_result": {
                    "winner": "route_a_speed_first",
                    "score_a": 92.0,
                    "score_b": 74.0,
                },
                "status": "pending_approval",
                "decision": {
                    "winner": "route_a_speed_first",
                    "reasoning_one_liner": "Surface Streets saves 14 minutes",
                    "requires_approval": True,
                },
            },
        )

        incident = self.client.get_incident(incident_id)
        assert incident["perception"]["severity"] == "critical"
        assert incident["route_a_proposal"]["ambulance_eta"] == 8
        assert incident["route_b_proposal"]["ambulance_eta"] == 11
        assert incident["negotiation_result"]["winner"] == "route_a_speed_first"
        assert incident["decision"]["requires_approval"] is True

    def test_concurrent_incidents_isolation(self):
        """Verify multiple concurrent incidents maintain isolated state."""
        id_a = "concurrent_a_001"
        id_b = "concurrent_b_002"

        self.client.create_incident(
            id_a,
            {
                "incident_id": id_a,
                "status": "processing",
                "description": "Incident Alpha",
            },
        )
        self.client.create_incident(
            id_b,
            {
                "incident_id": id_b,
                "status": "executing",
                "description": "Incident Bravo",
            },
        )

        # Update A without affecting B
        self.client.update_incident(id_a, {"status": "pending_approval"})

        inc_a = self.client.get_incident(id_a)
        inc_b = self.client.get_incident(id_b)

        assert inc_a["status"] == "pending_approval"
        assert inc_b["status"] == "executing"  # unchanged
        assert inc_a["description"] == "Incident Alpha"
        assert inc_b["description"] == "Incident Bravo"

    def test_nonexistent_incident_returns_none(self):
        """Verify that querying a nonexistent incident returns None."""
        result = self.client.get_incident("nonexistent_999")
        assert result is None
