from typing import Dict, Any, List

class GridTrafficSimulator:
    """Lightweight grid traffic simulator for evaluating route proposals."""
    
    def __init__(self):
        # A simple grid of intersections representing the city
        self.intersections = {
            "I1": {"name": "5th Ave & Main St", "congestion": 0.8},
            "I2": {"name": "Broadway & Main St", "congestion": 0.6},
            "I3": {"name": "Broadway & Elm St", "congestion": 0.4},
            "I4": {"name": "Highway 101 Onramp", "congestion": 0.3},
            "I5": {"name": "Highway 101 Exit", "congestion": 0.2},
            "I6": {"name": "County General Hospital Entrance", "congestion": 0.5}
        }
        
    def simulate_route(self, route_name: str, base_eta: int) -> Dict[str, Any]:
        """
        Simulate travel along a proposed route.
        
        Returns:
            ambulance_arrival_time: int (minutes)
            vehicles_delayed: int (count of non-emergency vehicles)
            avg_delay: int (minutes per vehicle)
            collision_risk: float
            heatmap: str (URL or visualization reference)
        """
        # Standardized deterministic outputs based on the route classification
        name = route_name.lower()
        if "surface" in name or "street" in name:
            # Surface Streets Route: faster for ambulance, higher collateral delay
            ambulance_arrival_time = max(5, int(base_eta * 0.4))  # e.g., 22 * 0.4 = 8 mins
            vehicles_delayed = 12
            avg_delay = 2
            collision_risk = 0.3
            heatmap_url = "https://storage.googleapis.com/civitas-demo/heatmaps/surface_streets.png"
        else:
            # Highway/Alternative Route: slower for ambulance, lower collateral delay
            ambulance_arrival_time = max(5, int(base_eta * 0.5))  # e.g., 22 * 0.5 = 11 mins
            vehicles_delayed = 3
            avg_delay = 4
            collision_risk = 0.1
            heatmap_url = "https://storage.googleapis.com/civitas-demo/heatmaps/highway.png"
            
        return {
            "ambulance_arrival_time": ambulance_arrival_time,
            "vehicles_delayed": vehicles_delayed,
            "avg_delay": avg_delay,
            "collision_risk": collision_risk,
            "heatmap": heatmap_url
        }
