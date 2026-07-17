import os
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Maximum allowed simulation execution time in seconds
SIMULATION_DEADLINE_SECONDS = 3.0

try:
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend for server/CLI compatibility
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
            "I6": {"name": "County General Hospital Entrance", "congestion": 0.5},
        }

    def generate_heatmap_image(
        self,
        route_name: str,
        deadline: float = None,
        vehicles_impacted: int = 12,
        incident_id: str = None,
    ) -> str:
        """
        Generate a visual PNG heatmap of network congestion using matplotlib.
        Returns mock URL if deadline exceeded or matplotlib unavailable.
        """
        if not HAS_PLOT:
            return f"mock_url_for_{route_name.lower()}_heatmap.png"

        # Early exit if past deadline
        if deadline is not None and time.monotonic() > deadline:
            logger.warning("Heatmap generation skipped: simulation deadline exceeded")
            return f"mock_url_for_{route_name.lower()}_heatmap.png"

        try:
            # Create a 10x10 congestion grid
            grid_size = 10
            # Base congestion level proportional to vehicles_impacted
            base_congestion = min(0.8, max(0.15, vehicles_impacted / 20.0))
            data = np.random.rand(grid_size, grid_size) * base_congestion

            # Trace paths and add congestion impact
            if "surface" in route_name.lower() or "street" in route_name.lower():
                # Surface streets has higher congestion spread
                for i in range(grid_size):
                    data[i, i] = base_congestion + 0.1
                    if i > 0:
                        data[i - 1, i] = base_congestion * 0.7
                    if i < grid_size - 1:
                        data[i + 1, i] = base_congestion * 0.6
            else:
                # Highway alternative has isolated corridor congestion
                for i in range(grid_size):
                    data[0, i] = base_congestion + 0.15
                    data[i, grid_size - 1] = base_congestion + 0.15

            # Set up matplotlib figure
            plt.figure(figsize=(4, 4))
            plt.imshow(data, cmap="YlOrRd", interpolation="bilinear")
            plt.title(f"{route_name} - {vehicles_impacted} Delayed", fontsize=8)
            plt.axis("off")

            # Save to agents/data/heatmaps/ or data/heatmaps/
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            heatmap_dir = os.path.join(base_dir, "data", "heatmaps")
            os.makedirs(heatmap_dir, exist_ok=True)

            prefix = f"{incident_id}_" if incident_id else ""
            file_name = f"{prefix}{route_name.lower().replace(' ', '_')}_heatmap.png"
            file_path = os.path.join(heatmap_dir, file_name)

            plt.savefig(file_path, bbox_inches="tight", dpi=100)
            plt.close()

            return f"file:///{file_path.replace(os.sep, '/')}"
        except Exception:
            return f"mock_url_for_{route_name.lower()}_heatmap.png"

    def simulate_route(
        self,
        route_name: str,
        base_eta: int,
        deadline: float = None,
        proposal_eta: int = None,
        proposal_vehicles: int = None,
        proposal_delay: int = None,
        incident_id: str = None,
    ) -> Dict[str, Any]:
        """
        Simulate travel along a proposed route.

        Args:
            route_name: Name of the route corridor
            base_eta: Baseline ETA in minutes without optimization
            deadline: Monotonic time deadline (from time.monotonic()). If exceeded,
                      heatmap generation is skipped but metrics are still computed.
            proposal_eta: Proposal ETA override from route agents.
            proposal_vehicles: Vehicles impacted override from route agents.
            proposal_delay: Average vehicle delay override from route agents.
            incident_id: Active incident ID context for unique file outputs.

        Returns:
            ambulance_arrival_time: int (minutes)
            vehicles_delayed: int (count of non-emergency vehicles)
            avg_delay: int (minutes per vehicle)
            collision_risk: float
            heatmap: str (URL or local file path)
            execution_time_ms: float (wall-clock execution time)
        """
        t0 = time.monotonic()
        name = route_name.lower()

        # 1. Determine simulator metrics
        if proposal_eta is not None:
            ambulance_arrival_time = proposal_eta
            vehicles_delayed = proposal_vehicles
            avg_delay = proposal_delay
            collision_risk = 0.25 if "surface" in name or "street" in name else 0.12
        else:
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

        # 2. Generate visual heatmap file (respects deadline)
        heatmap_path = self.generate_heatmap_image(
            route_name,
            deadline=deadline,
            vehicles_impacted=vehicles_delayed,
            incident_id=incident_id,
        )

        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.info(f"simulate_route({route_name}) completed in {elapsed_ms:.1f}ms")

        return {
            "ambulance_arrival_time": ambulance_arrival_time,
            "vehicles_delayed": vehicles_delayed,
            "avg_delay": avg_delay,
            "collision_risk": collision_risk,
            "heatmap": heatmap_path,
            "execution_time_ms": elapsed_ms,
        }
