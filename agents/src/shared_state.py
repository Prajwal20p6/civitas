"""
Global shared session state manager for CIVITAS agent pipelines.

Supports incident-scoped sessions so multiple incidents can be processed
concurrently without state collision. Thread-safe via a lock on the
session registry.
"""
import threading
from typing import Any, Dict, Optional
from pydantic import BaseModel


class IncidentState(BaseModel):
    """Shared state across all agents for a single incident."""

    incident_id: str
    perception_output: Optional[Dict[str, Any]] = None
    route_a_proposal: Optional[Dict[str, Any]] = None
    route_b_proposal: Optional[Dict[str, Any]] = None
    negotiation_result: Optional[Dict[str, Any]] = None
    explainability_output: Optional[Dict[str, Any]] = None
    approval_status: str = "pending"  # pending, approved, denied, timeout
    execution_status: str = "not_started"  # not_started, executing, completed, failed


class SessionStateManager:
    """Manage shared session state for a single incident (backed by Firestore in production)."""

    def __init__(self, incident_id: str):
        self.incident_id = incident_id
        self.state = IncidentState(incident_id=incident_id)
        self._lock = threading.Lock()

    def read(self, key: str) -> Any:
        """Read a value from shared state."""
        with self._lock:
            return getattr(self.state, key, None)

    def write(self, key: str, value: Any):
        """Write a value to shared state."""
        with self._lock:
            setattr(self.state, key, value)

    def snapshot(self) -> Dict[str, Any]:
        """Return a serializable snapshot of the current state."""
        with self._lock:
            return self.state.model_dump()

    def export_to_firestore(self):
        """Persist state to Firestore (placeholder for production wiring)."""
        pass


# --- Incident-Scoped Session Registry ---

_registry: Dict[str, SessionStateManager] = {}
_registry_lock = threading.Lock()


def get_session_state(incident_id: str = "default") -> SessionStateManager:
    """
    Get or create a SessionStateManager for the given incident_id.

    Thread-safe: multiple concurrent pipelines can each have their own
    isolated state without collision.

    Args:
        incident_id: Unique incident identifier. Defaults to 'default' for
                      backwards compatibility with single-incident CLI usage.

    Returns:
        SessionStateManager instance scoped to the given incident.
    """
    with _registry_lock:
        if incident_id not in _registry:
            _registry[incident_id] = SessionStateManager(incident_id)
        return _registry[incident_id]


def clear_session(incident_id: str):
    """Remove a completed incident's state from the registry."""
    with _registry_lock:
        _registry.pop(incident_id, None)


def list_active_sessions() -> list:
    """Return a list of all active incident session IDs."""
    with _registry_lock:
        return list(_registry.keys())
