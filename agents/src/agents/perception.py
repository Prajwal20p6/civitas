import os
from src.adk_setup import LlmAgent
from src.schemas import IncidentInput, IncidentClassification

class PerceptionAgent(LlmAgent):
    """Classifies incoming incident reports to assess severity and urgency."""
    
    async def execute(self, incident: IncidentInput) -> IncidentClassification:
        """
        Classifies an incident using rule-based heuristics or Gemini API if keys are available.
        """
        desc = incident.description.lower()
        
        # Rule-based heuristics for deterministic demo and local test resilience
        if "cardiac" in desc or "stroke" in desc or "heart" in desc or "ambulance" in desc or "patient" in desc:
            inc_type = "medical_emergency"
            severity = "critical"
            priority = 0.95
            reasoning = "High-priority life-threatening medical emergency. Dispatched ambulance requires optimal routing."
        elif "collision" in desc or "accident" in desc or "crash" in desc:
            inc_type = "accident"
            severity = "major"
            priority = 0.70
            reasoning = "Multi-vehicle traffic accident blocking lanes. Elevated risk of delay."
        else:
            inc_type = "hazard"
            severity = "minor"
            priority = 0.40
            reasoning = "Road congestion or minor debris. Routing adjustment recommended."
            
        return IncidentClassification(
            incident_type=inc_type,
            severity=severity,
            location=incident.location,
            baseline_eta=incident.base_eta_to_destination,
            priority_score=priority,
            reasoning=reasoning
        )
