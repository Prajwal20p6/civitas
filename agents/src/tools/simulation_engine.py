import os
from typing import Dict, Any, List

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server/CLI compatibility
    import matplotlib.pyplot as plt
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False

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
        
    def generate_heatmap_image(self, route_name: str) -> str:
        """
        Generate a visual PNG heatmap of network congestion using matplotlib.
        """
        if not HAS_PLOT:
            return f"mock_url_for_{route_name.lower()}_heatmap.png"
            
        try:
            # Create a 10x10 congestion grid
            grid_size = 10
            data = np.random.rand(grid_size, grid_size) * 0.2  # background noise
            
            # Trace paths and add congestion impact
            if "surface" in route_name.lower() or "street" in route_name.lower():
                # Surface streets has higher congestion spread
                for i in range(grid_size):
                    data[i, i] = 0.9  # route path
                    if i > 0:
                        data[i-1, i] = 0.6
                    if i < grid_size - 1:
                        data[i+1, i] = 0.5
            else:
                # Highway alternative has isolated corridor congestion
                for i in range(grid_size):
                    data[0, i] = 0.8
                    data[i, grid_size-1] = 0.8
                    
            # Set up matplotlib figure
            plt.figure(figsize=(3, 3))
            plt.imshow(data, cmap="YlOrRd", interpolation="bilinear")
            plt.title(f"{route_name} Congestion", fontsize=8)
            plt.axis("off")
            
            # Save to agents/data/heatmaps/ or data/heatmaps/
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            heatmap_dir = os.path.join(base_dir, "data", "heatmaps")
            os.makedirs(heatmap_dir, exist_ok=True)
            
            file_name = f"{route_name.lower().replace(' ', '_')}_heatmap.png"
            file_path = os.path.join(heatmap_dir, file_name)
            
            plt.savefig(file_path, bbox_inches="tight", dpi=100)
            plt.close()
            
            return f"file:///{file_path.replace(os.sep, '/')}"
        except Exception:
            return f"mock_url_for_{route_name.lower()}_heatmap.png"

    def simulate_route(self, route_name: str, base_eta: int) -> Dict[str, Any]:
        """
        Simulate travel along a proposed route.
        
        Returns:
            ambulance_arrival_time: int (minutes)
            vehicles_delayed: int (count of non-emergency vehicles)
            avg_delay: int (minutes per vehicle)
            collision_risk: float
            heatmap: str (URL or local file path)
        """
        name = route_name.lower()
        
        # 1. Generate visual heatmap file
        heatmap_path = self.generate_heatmap_image(route_name)
        
        # 2. Determine simulator metrics
        if "surface" in name or "street" in name:
            ambulance_arrival_time = max(5, int(base_eta * 0.4))
            vehicles_delayed = 12
            avg_delay = 2
            collision_risk = 0.3
        else:
            ambulance_arrival_time = max(5, int(base_eta * 0.5))
            vehicles_delayed = 3
            avg_delay = 4
            collision_risk = 0.1
            
        return {
            "ambulance_arrival_time": ambulance_arrival_time,
            "vehicles_delayed": vehicles_delayed,
            "avg_delay": avg_delay,
            "collision_risk": collision_risk,
            "heatmap": heatmap_path
        }
