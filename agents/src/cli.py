import asyncio
import json
import os
import sys
from src.agents.orchestrator import OrchestratorAgent
from src.schemas import IncidentInput


async def main():
    print("==================================================")
    print("   CIVITAS Emergency Traffic Coordinator CLI       ")
    print("==================================================")

    if len(sys.argv) < 2:
        print("Usage: python -m src.cli <path_to_scenarios_json>")
        return

    scenarios_path = sys.argv[1]

    # Resolve path fallback if run inside agents or root folder
    if not os.path.exists(scenarios_path):
        if scenarios_path.startswith("agents/"):
            scenarios_path = scenarios_path.replace("agents/", "", 1)
        else:
            scenarios_path = os.path.join("agents", scenarios_path)

    if not os.path.exists(scenarios_path):
        print(
            f"Error: Scenarios file not found at {sys.argv[1]} or resolved path {scenarios_path}"
        )
        return

    with open(scenarios_path, "r") as f:
        data_loaded = json.load(f)

    if isinstance(data_loaded, dict):
        scenarios = [data_loaded]
    else:
        scenarios = data_loaded

    orchestrator = OrchestratorAgent()

    # Run only first 3 cases to ensure execution is fast and concise
    for idx, scenario in enumerate(scenarios[:3], 1):
        print(
            f"\n[Scenario {idx}] Ingesting {scenario.get('incident_type', 'emergency')}"
        )
        print(f"Description: {scenario.get('description')}")

        # Determine fallback parameters to support basic test data files
        location_raw = scenario.get("location") or {"lat": 37.4219, "lng": -122.0840}
        location = {k: float(v) for k, v in location_raw.items() if k in ["lat", "lng"]}
        current_time = scenario.get("current_time") or "2026-07-15T09:30:00Z"
        base_eta = scenario.get(
            "base_eta_to_destination", scenario.get("baseline_eta_minutes", 22)
        )

        incident_in = IncidentInput(
            incident_type=scenario.get("incident_type", "emergency_911"),
            description=scenario.get("description"),
            location=location,
            current_time=current_time,
            base_eta_to_destination=base_eta,
        )

        print("Running Agents Coordinator...")
        decision = await orchestrator.execute(incident_in)

        print("\n--- Pipeline Decision Results ---")
        print(f"Winner: {decision.winner}")
        print(
            f"Requires Operator Approval: {'YES' if decision.requires_approval else 'NO'}"
        )
        print(f"Explanation: {decision.reasoning_summary}")
        print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
