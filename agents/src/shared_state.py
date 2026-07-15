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
    approval_status: str = "pending"  # pending, approved, denied
    execution_status: str = "not_started"  # not_started, executing, completed

class SessionStateManager:
    """Manage shared session state (backed by Firestore in production)."""
    
    def __init__(self, incident_id: str):
        self.incident_id = incident_id
        self.state = IncidentState(incident_id=incident_id)
    
    def read(self, key: str) -> Any:
        """Read a value from shared state."""
        return getattr(self.state, key)
    
    def write(self, key: str, value: Any):
        """Write a value to shared state."""
        setattr(self.state, key, value)
    
    def export_to_firestore(self):
        """Persist state to Firestore."""
        pass

# Global state manager (in production, keyed by incident_id)
_session_state: Optional[SessionStateManager] = None

def get_session_state() -> SessionStateManager:
    global _session_state
    if _session_state is None:
        _session_state = SessionStateManager("incident_001")
    return _session_state
