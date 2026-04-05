"""
HERE Maps API client wrapper.
Provides clean interface for fetching public transport directions.
API Documentation: https://developer.here.com/documentation/routing-api/8.9.0/dev_guide/index.html
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config


class HereClient:
    """
    Wrapper for HERE Routing API (v8).
    Handles authentication, request building, and error handling.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client with an API key.

        Args:
            api_key: HERE API key. If None, uses Config.HERE_API_KEY
        """
        self.api_key = api_key or Config.HERE_API_KEY
        if not self.api_key:
            raise ValueError("HERE API key is required")

        self.base_url = "https://router.hereapi.com/v8/routes"
        self.session = requests.Session()

    def get_routes(
        self,
        origin: str,
        destination: str,
        departure_time: Optional[datetime] = None,
        alternatives: bool = True,
        transit_mode: str = "publicTransport"
    ) -> List[Dict]:
        """
        Fetch public transport routes from HERE Routing API.

        Args:
            origin: Starting location (address, "lat,lon", or place name)
            destination: End location (address, "lat,lon", or place name)
            departure_time: When to depart (None = now)
            alternatives: Whether to return multiple route options
            transit_mode: Must be "publicTransport" for transit

        Returns:
            List of route dictionaries formatted to match Google Maps structure
            (for compatibility with existing parser)

        Raises:
            Exception: If the API request fails
        """
        try:
            # Build request parameters
            params = {
                "apiKey": self.api_key,
                "transportMode": transit_mode,
                "origin": origin,
                "destination": destination,
                "return": "summary,actions,fare,travelSummary,stations"
            }

            # Add departure time (HERE uses 'departureTime' in ISO 8601)
            if departure_time:
                # Format: 2024-01-15T09:30:00
                params["departureTime"] = departure_time.isoformat()

            # Request multiple alternatives
            if alternatives:
                params["routingMode"] = "fast"  # Fastest routes
                # HERE returns multiple routes by default when alternatives requested
                params["alternatives"] = str(alternatives).lower()

            # Make API request
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Check for API errors in response body
            if "error" in data:
                error_desc = data["error"].get("description", "Unknown error")
                raise Exception(f"HERE API error: {error_desc}")

            # Convert HERE response format to Google Maps-like format
            # This allows us to reuse the existing RouteParser
            google_format_routes = self._convert_to_google_format(data)

            if not google_format_routes:
                raise ValueError(
                    f"No routes found from '{origin}' to '{destination}'. "
                    "Check that these locations are valid and public transport is available."
                )

            return google_format_routes

        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    raise ValueError(
                        "Invalid HERE API key. Please check your API key in .env file."
                    )
                elif e.response.status_code == 403:
                    raise ValueError(
                        "API key not authorized for Routing API. "
                        "Enable Routing API in HERE Developer Portal."
                    )
                elif e.response.status_code == 429:
                    raise ValueError(
                        "API quota exceeded. Please check your usage limits."
                    )
                else:
                    raise ValueError(f"HERE API HTTP error {e.response.status_code}: {e.response.text}")
            else:
                raise Exception(f"Failed to fetch routes: {str(e)}")

    def _convert_to_google_format(self, here_data: Dict) -> List[Dict]:
        """
        Convert HERE API response to Google Maps-like format.
        This allows reusing the existing RouteParser without modification.

        Args:
            here_data: Raw response from HERE API

        Returns:
            List of route dictionaries in Google Maps format
        """
        routes = []
        for route in here_data.get("routes", []):
            google_route = {
                "summary": route.get("id", "HERE Route"),
                "legs": [self._convert_leg(route)],
                "fare": self._convert_fare(route)
            }
            routes.append(google_route)

        return routes

    def _convert_leg(self, route: Dict) -> Dict:
        """
        Convert a HERE route to a Google Maps leg format.

        HERE structure:
        - route['sections'] = list of journey segments (similar to steps/legs)
        - Each section has: travelMode, departure/arrival, duration, distance

        Google Maps structure:
        - leg: { duration, distance, steps[] }
        - Each step: { travel_mode, duration, distance, html_instructions, transit_details? }
        """
        sections = route.get("sections", [])

        # Calculate total duration and distance from all sections
        total_duration_value = sum(section.get("duration", 0) for section in sections)
        total_distance_value = sum(section.get("length", 0) for section in sections)

        # Get departure and arrival times
        departure_time = None
        arrival_time = None
        if sections:
            first_section = sections[0]
            last_section = sections[-1]

            dep = first_section.get("departure", {}).get("place", {})
            arr = last_section.get("arrival", {}).get("place", {})

            if "estimatedTime" in first_section.get("departure", {}):
                departure_time = datetime.fromtimestamp(first_section["departure"]["estimatedTime"] / 1000)
            if "estimatedTime" in last_section.get("arrival", {}):
                arrival_time = datetime.fromtimestamp(last_section["arrival"]["estimatedTime"] / 1000)

        # Convert sections to steps
        steps = []
        total_walking_distance = 0
        total_walking_time = 0

        for section in sections:
            transport_mode = section.get("transport", {}).get("mode", "unknown").lower()

            # Get distance and duration
            length_meters = section.get("length", 0)
            duration_seconds = section.get("duration", 0)

            # Build instruction based on transport mode
            if transport_mode == "walk":
                instruction = f"Walk to {section.get('arrival', {}).get('place', {}).get('name', 'destination')}"
                total_walking_distance += length_meters
                total_walking_time += duration_seconds
            elif transport_mode == "publicTransport":
                # Get transit details
                transit_details = section.get("transport", {})
                line = transit_details.get("name", "Public Transport")
                vehicle_type = transit_details.get("type", "BUS")  # BUS, SUBWAY, RAIL, etc.

                dep_stop = section.get("departure", {}).get("place", {}).get("name", "")
                arr_stop = section.get("arrival", {}).get("place", {}).get("name", "")

                instruction = f"Take {line} from {dep_stop} to {arr_stop}"

                step = {
                    "travel_mode": "TRANSIT",
                    "duration": {"text": self._format_duration(duration_seconds), "value": duration_seconds},
                    "distance": {"text": self._format_distance(length_meters), "value": length_meters},
                    "html_instructions": instruction,
                    "transit_details": {
                        "line": {
                            "name": line,
                            "vehicle": {"type": vehicle_type}
                        },
                        "departure_stop": {"name": dep_stop},
                        "arrival_stop": {"name": arr_stop}
                    }
                }
                steps.append(step)
                continue  # Skip adding as walking step below
            else:
                # Other modes: bicycle, car, etc.
                instruction = f"{transport_mode.capitalize()} section"

            step = {
                "travel_mode": transport_mode.upper(),
                "duration": {"text": self._format_duration(duration_seconds), "value": duration_seconds},
                "distance": {"text": self._format_distance(length_meters), "value": length_meters},
                "html_instructions": instruction
            }
            steps.append(step)

        # Build leg in Google format
        leg = {
            "duration": {"text": self._format_duration(total_duration_value), "value": total_duration_value},
            "distance": {"text": self._format_distance(total_distance_value), "value": total_distance_value},
            "steps": steps
        }

        if departure_time:
            leg["departure_time"] = {"value": int(departure_time.timestamp())}
        if arrival_time:
            leg["arrival_time"] = {"value": int(arrival_time.timestamp())}

        return leg

    def _convert_fare(self, route: Dict) -> Optional[Dict]:
        """Extract fare information if available."""
        # HERE fare info is in route['pricing'] if available
        pricing = route.get("pricing", [])
        if pricing:
            # Find the total fare
            for price in pricing:
                if price.get("priceType") == "total":
                    currency = price.get("currencyCode", "USD")
                    amount = price.get("price", 0)
                    return {"text": f"{currency} {amount:.2f}", "value": amount}
        return None

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds to human-readable duration (e.g., '35 min')"""
        minutes = seconds // 60 if seconds else 0
        if minutes < 60:
            return f"{minutes} min"
        else:
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{hours} hr"
            else:
                return f"{hours} hr {mins} min"

    @staticmethod
    def _format_distance(meters: float) -> str:
        """Format meters to human-readable distance (e.g., '8.2 km')"""
        km = meters / 1000 if meters else 0
        if km >= 1:
            return f"{km:.1f} km"
        else:
            return f"{int(meters)} m"

    def validate_location(self, location: str) -> bool:
        """
        Basic validation for location strings.

        Args:
            location: Location string to validate

        Returns:
            True if location appears valid
        """
        if not location or not location.strip():
            return False
        if len(location) < 2 or len(location) > 200:
            return False
        return True