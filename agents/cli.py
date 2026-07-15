import asyncio
import json
import os
from src.agents.orchestrator import OrchestratorAgent
from src.schemas import IncidentInput

async def main():
    print("==================================================")
    print("   CIVITAS Emergency Traffic Coordinator CLI       ")
    print("==================================================")
    
    # Resolve the scenarios path
    scenarios_path = os.path.join("tests", "fixtures", "test_scenarios.json")
    if not os.path.exists(scenarios_path):
        scenarios_path = os.path.join("agents", "tests", "fixtures", "test_scenarios.json")
        
    if not os.path.exists(scenarios_path):
        print(f"Error: test_scenarios.json not found.")
        return
        
    with open(scenarios_path, "r") as f:
        scenarios = json.load(f)
        
    orchestrator = OrchestratorAgent()
    
    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n[Scenario {idx}] Ingesting {scenario['incident_type']}")
        print(f"Description: {scenario['description']}")
        print(f"Location: {scenario['location']}")
        print(f"Base ETA: {scenario['base_eta_to_destination']} mins")
        
        incident_in = IncidentInput(
            incident_type=scenario['incident_type'],
            description=scenario['description'],
            location=scenario['location'],
            current_time=scenario['current_time'],
            base_eta_to_destination=scenario['base_eta_to_destination']
        )
        
        print("Running Agents Coordinator...")
        decision = await orchestrator.execute(incident_in)
        
        print("\n--- Pipeline Decision Results ---")
        print(f"Winner: {decision.winner}")
        print(f"Requires Operator Approval: {'YES' if decision.requires_approval else 'NO'}")
        print(f"Explanation: {decision.reasoning_summary}")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
