"""Football-specific Sports API module."""
from server.services.sports.football.client import FootballClient
from server.services.sports.football.mapper import FootballMapper

__all__ = ["FootballClient", "FootballMapper"]
