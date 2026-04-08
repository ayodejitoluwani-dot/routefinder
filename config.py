"""
Configuration management for the Public Transport Route Finder.
Supports multiple map providers (Google Maps, HERE API) and allows easy addition of new APIs.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""

    # Map provider selection: 'google' or 'here'
    MAPS_PROVIDER = os.getenv("MAPS_PROVIDER", "google").lower()

    # Google Maps API
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    # HERE API
    HERE_API_KEY = os.getenv("HERE_API_KEY")

    # Default settings
    DEFAULT_TRANSIT_MODE = "transit"
    MAX_ROUTES = 5

    # Scoring weights (must sum to 1.0)
    SCORING_WEIGHTS = {
        'duration': 0.4,
        'transfers': 0.3,
        'walking': 0.3
    }

    # Storage
    STORAGE_PATH = os.getenv("STORAGE_PATH", "data/reviews.json")

    @classmethod
    def validate(cls):
        """Validate configuration based on selected provider"""
        provider = cls.MAPS_PROVIDER

        if provider == 'google':
            if not cls.GOOGLE_MAPS_API_KEY:
                raise ValueError(
                    "GOOGLE_MAPS_API_KEY not set. "
                    "Please add it to your .env file or set MAPS_PROVIDER=here to use HERE API instead."
                )
        elif provider == 'here':
            if not cls.HERE_API_KEY:
                raise ValueError(
                    "HERE_API_KEY not set. "
                    "Please add it to your .env file or set MAPS_PROVIDER=google to use Google Maps instead."
                )
        else:
            raise ValueError(
                f"Invalid MAPS_PROVIDER: '{provider}'. "
                "Must be 'google' or 'here'."
            )

        return True

    @classmethod
    def get_api_key(cls):
        """Get the API key for the selected provider"""
        if cls.MAPS_PROVIDER == 'google':
            return cls.GOOGLE_MAPS_API_KEY
        elif cls.MAPS_PROVIDER == 'here':
            return cls.HERE_API_KEY
        return None

##This is the part of the code that selects the api to choose
