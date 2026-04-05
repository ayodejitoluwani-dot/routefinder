"""
Factory for creating map provider clients.
Returns an instance of the configured provider (Google Maps or HERE).
"""
from typing import Optional
from config import Config
from google_maps_client import GoogleMapsClient
from here_client import HereClient


class ClientFactory:
    """Factory for creating map API clients based on configuration."""

    @staticmethod
    def create_client():
        """
        Create and return a map client based on MAPS_PROVIDER config.

        Returns:
            An instance of GoogleMapsClient or HereClient

        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        provider = Config.MAPS_PROVIDER

        if provider == 'google':
            return GoogleMapsClient(Config.GOOGLE_MAPS_API_KEY)
        elif provider == 'here':
            return HereClient(Config.HERE_API_KEY)
        else:
            raise ValueError(
                f"Unsupported map provider: '{provider}'. "
                "Supported: 'google', 'here'"
            )

    @staticmethod
    def get_provider_name() -> str:
        """Get the current provider name (for display)."""
        provider = Config.MAPS_PROVIDER
        names = {
            'google': 'Google Maps',
            'here': 'HERE Maps'
        }
        return names.get(provider, provider.title())