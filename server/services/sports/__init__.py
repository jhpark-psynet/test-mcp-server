"""Sports API client factory and modules."""
from typing import Union
from server.services.sports.basketball import BasketballClient
from server.services.sports.soccer import SoccerClient
from server.services.sports.volleyball import VolleyballClient

__all__ = ["SportsClientFactory", "BasketballClient", "SoccerClient", "VolleyballClient"]


class SportsClientFactory:
    """Factory for creating sport-specific API clients."""

    @staticmethod
    def create_client(sport: str) -> Union[BasketballClient, SoccerClient, VolleyballClient]:
        """Create a sport-specific API client.

        Args:
            sport: Sport name (basketball, soccer, volleyball)

        Returns:
            Sport-specific client instance

        Raises:
            ValueError: Unsupported sport
        """
        if sport == "basketball":
            return BasketballClient()
        elif sport == "soccer":
            return SoccerClient()
        elif sport == "volleyball":
            return VolleyballClient()
        else:
            raise ValueError(
                f"Unsupported sport: {sport}. "
                f"Must be one of: basketball, soccer, volleyball"
            )
