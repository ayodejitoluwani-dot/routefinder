"""
Google Maps API client wrapper.
Provides clean interface for fetching directions with error handling.
"""
import googlemaps
from datetime import datetime
from typing import Dict, List, Optional
from config import Config


class GoogleMapsClient:
    """
    Wrapper for Google Maps Directions API.
    Handles authentication, request building, and error handling.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client with an API key.

        Args:
            api_key: Google Maps API key. If None, uses Config.GOOGLE_MAPS_API_KEY
        """
        self.api_key = api_key or Config.GOOGLE_MAPS_API_KEY
        if not self.api_key:
            raise ValueError("Google Maps API key is required")

        self.client = googlemaps.Client(key=self.api_key)

    def get_routes(
        self,
        origin: str,
        destination: str,
        departure_time: Optional[datetime] = None,
        arrival_time: Optional[datetime] = None,
        alternatives: bool = True,
        transit_mode: str = Config.DEFAULT_TRANSIT_MODE,
        traffic_model: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch directions from Google Maps API.

        Args:
            origin: Starting location (address, place name, or lat/lng)
            destination: End location (address, place name, or lat/lng)
            departure_time: When to depart (None = now)
            arrival_time: When to arrive (mutually exclusive with departure_time)
            alternatives: Whether to return multiple route options
            transit_mode: Mode of transport ('transit', 'driving', 'walking', 'bicycling')
            traffic_model: Traffic model for driving mode ('best_guess', 'pessimistic', 'optimistic')

        Returns:
            List of route dictionaries from the API

        Raises:
            Exception: If the API request fails
        """
        try:
            # Build request parameters
            params = {
                'origin': origin,
                'destination': destination,
                'mode': transit_mode,
                'alternatives': alternatives
            }

            # Add time parameters
            if departure_time:
                params['departure_time'] = departure_time
            elif arrival_time:
                params['arrival_time'] = arrival_time

            # Add traffic model if specified (only for driving mode)
            if traffic_model and transit_mode == 'driving':
                params['traffic_model'] = traffic_model

            # Make API request
            response = self.client.directions(**params)

            if not response:
                raise ValueError(
                    f"No routes found from '{origin}' to '{destination}'. "
                    "Check that these locations are valid and public transit is available."
                )

            return response

        except googlemaps.exceptions.ApiError as e:
            error_message = str(e)
            if "API key not valid" in error_message:
                raise ValueError(
                    "Invalid Google Maps API key. Please check your API key in .env file."
                )
            elif "This API project is not authorized" in error_message:
                raise ValueError(
                    "API key not authorized for Directions API. "
                    "Enable Directions API in Google Cloud Console."
                )
            elif "over query limit" in error_message:
                raise ValueError(
                    "API quota exceeded. Please check your billing and usage limits."
                )
            else:
                raise Exception(f"Google Maps API error: {error_message}")

        except Exception as e:
            raise Exception(f"Failed to fetch routes: {str(e)}")

    def get_transit_modes(self) -> List[str]:
        """
        Get available transit modes.

        Returns:
            List of supported transit mode strings
        """
        return ['transit', 'driving', 'walking', 'bicycling']

    def validate_location(self, location: str) -> bool:
        """
        Check if a location string is valid (basic validation).

        Args:
            location: Location string to validate

        Returns:
            True if location appears valid (has content, reasonable length)
        """
        if not location or not location.strip():
            return False
        if len(location) < 2 or len(location) > 200:
            return False
        return True