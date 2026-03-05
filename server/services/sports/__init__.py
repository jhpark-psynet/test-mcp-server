"""Sports API client factory and modules."""
from typing import Dict, Type, Union

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.basketball import BasketballClient
from server.services.sports.soccer import SoccerClient
from server.services.sports.volleyball import VolleyballClient
from server.services.sports.baseball import BaseballClient

__all__ = [
    "SportsClientFactory",
    "BaseSportsClient",
    "BasketballClient",
    "SoccerClient",
    "VolleyballClient",
    "BaseballClient",
]


class SportsClientFactory:
    """Factory for creating sport-specific API clients.

    Uses a registry pattern for easy extension. To add a new sport:
    1. Create the sport module with client.py, endpoints.py, mapper.py
    2. Register it: SportsClientFactory.register("newsport", NewSportClient)
    """

    # Class-level registry mapping sport names to client classes
    _registry: Dict[str, Type[BaseSportsClient]] = {
        "basketball": BasketballClient,
        "soccer": SoccerClient,
        "volleyball": VolleyballClient,
        "baseball": BaseballClient,
    }

    # Singleton instances - reused across requests to preserve per-instance caches
    _instances: Dict[str, BaseSportsClient] = {}

    @classmethod
    def register(cls, sport: str, client_class: Type[BaseSportsClient]) -> None:
        """Register a new sport client.

        Args:
            sport: Sport name identifier
            client_class: Client class that extends BaseSportsClient
        """
        cls._registry[sport] = client_class
        cls._instances.pop(sport, None)  # Clear cached instance when re-registering

    @classmethod
    def unregister(cls, sport: str) -> None:
        """Unregister a sport client.

        Args:
            sport: Sport name to remove

        Raises:
            KeyError: If sport not registered
        """
        del cls._registry[sport]
        cls._instances.pop(sport, None)

    @classmethod
    def list_sports(cls) -> list[str]:
        """List all registered sports.

        Returns:
            List of sport name strings
        """
        return list(cls._registry.keys())

    @classmethod
    def create_client(
        cls, sport: str
    ) -> Union[BasketballClient, SoccerClient, VolleyballClient, BaseballClient]:
        """Return a cached sport-specific API client, creating it if needed.

        Clients are singletons per sport so per-instance caches (e.g.
        BaseballClient._total_info_cache) persist across requests.

        Args:
            sport: Sport name (basketball, soccer, volleyball, baseball)

        Returns:
            Sport-specific client instance (reused on subsequent calls)

        Raises:
            ValueError: Unsupported sport
        """
        if sport not in cls._registry:
            available = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(
                f"Unsupported sport: {sport}. "
                f"Available: {available}"
            )

        if sport not in cls._instances:
            cls._instances[sport] = cls._registry[sport]()
        return cls._instances[sport]
