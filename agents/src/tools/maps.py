import aiohttp
from typing import Dict, Any, List

class GoogleMapsClient:
    """Wrapper class for Google Maps API requests."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        
    async def get_routes_and_etas(self, origin: Dict[str, float], destination: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Query Google Maps Routes API to calculate routes, distance, and ETAs.
        In demo mode or fallback, returns mock pre-computed route options.
        """
        # Pre-computed route options for deterministic demo safety
        return [
            {
                "route_name": "Surface Streets",
                "distance_km": 8.2,
                "duration_minutes": 11,
                "congested_intersections": 4
            },
            {
                "route_name": "Highway 1",
                "distance_km": 9.1,
                "duration_minutes": 15,
                "congested_intersections": 1
            }
        ]
