"""Volleyball-specific Sports API client."""
from typing import Dict, List, Any, Optional
import logging

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.volleyball.mapper import VolleyballMapper
from server.services.sports.volleyball.endpoints import VOLLEYBALL_ENDPOINTS
from server.services.sports.volleyball.mock_data import (
    MOCK_VOLLEYBALL_GAMES,
    MOCK_VOLLEYBALL_TEAM_STATS,
    MOCK_VOLLEYBALL_PLAYER_STATS,
)

logger = logging.getLogger(__name__)


class VolleyballClient(BaseSportsClient):
    """Volleyball Sports API client."""

    def __init__(self):
        """Initialize volleyball API client."""
        super().__init__()
        self.mapper = VolleyballMapper()

    def get_sport_name(self) -> str:
        """Return the sport name."""
        return "volleyball"

    @property
    def endpoint_config(self):
        """Return volleyball endpoint configuration."""
        return VOLLEYBALL_ENDPOINTS

    async def get_games_by_sport(self, date: str) -> List[Dict[str, Any]]:
        """Get volleyball games for a specific date."""
        if len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid date format: {date}. Must be YYYYMMDD")

        if self.use_mock:
            key = f"{date}_volleyball"
            games = MOCK_VOLLEYBALL_GAMES.get(key, [])
            logger.info(f"[MOCK] Retrieved {len(games)} volleyball games for {date}")
            return games

        params = {
            "search_date": date,
            "compe": "volleyball",
            "fmt": "json",
        }
        try:
            endpoint = self._get_endpoint_for_operation("games")
            response = await self._make_request(endpoint, params)
            games = self.mapper.map_games_list(response)
            logger.info(f"[REAL API] Retrieved {len(games)} volleyball games for {date}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch volleyball games from API: {e}")
            raise

    async def get_team_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get team statistics for a volleyball game."""
        if self.use_mock:
            stats = MOCK_VOLLEYBALL_TEAM_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            logger.info(f"[MOCK] Retrieved volleyball team stats for game {game_id}")
            return stats

        params = {"game_id": game_id}
        try:
            endpoint = self._get_endpoint_for_operation("team_stats")
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_team_stats_list(response)
            if not stats:
                raise ValueError(f"No team stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved volleyball team stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch volleyball team stats from API: {e}")
            raise

    async def get_player_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get player statistics for a volleyball game."""
        if self.use_mock:
            stats = MOCK_VOLLEYBALL_PLAYER_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            logger.info(f"[MOCK] Retrieved volleyball player stats for game {game_id}")
            return stats

        params = {"game_id": game_id}
        try:
            endpoint = self._get_endpoint_for_operation("player_stats")
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_player_stats_list(response)
            if not stats:
                raise ValueError(f"No player stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved volleyball player stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch volleyball player stats from API: {e}")
            raise
