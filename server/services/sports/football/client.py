"""Football-specific Sports API client."""
from typing import Dict, List, Any, Optional
import logging

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.football.mapper import FootballMapper
from server.services.sports.football.endpoints import FOOTBALL_ENDPOINTS
from server.services.sports.football.mock_data import (
    MOCK_FOOTBALL_GAMES,
    MOCK_FOOTBALL_TEAM_STATS,
    MOCK_FOOTBALL_PLAYER_STATS,
)

logger = logging.getLogger(__name__)


class FootballClient(BaseSportsClient):
    """Football Sports API client."""

    def __init__(self):
        """Initialize football API client."""
        super().__init__()
        self.mapper = FootballMapper()

    def get_sport_name(self) -> str:
        """Return the sport name."""
        return "football"

    @property
    def endpoint_config(self):
        """Return football endpoint configuration."""
        return FOOTBALL_ENDPOINTS

    async def get_games_by_sport(self, date: str) -> List[Dict[str, Any]]:
        """Get football games for a specific date."""
        if len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid date format: {date}. Must be YYYYMMDD")

        if self.use_mock:
            key = f"{date}_football"
            games = MOCK_FOOTBALL_GAMES.get(key, [])
            logger.info(f"[MOCK] Retrieved {len(games)} football games for {date}")
            return games

        params = {
            "search_date": date,
            "compe": "football",
            "fmt": "json",
        }
        try:
            endpoint = self._get_endpoint_for_operation("games")
            response = await self._make_request(endpoint, params)
            games = self.mapper.map_games_list(response)
            logger.info(f"[REAL API] Retrieved {len(games)} football games for {date}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch football games from API: {e}")
            raise

    async def get_team_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get team statistics for a football game."""
        if self.use_mock:
            stats = MOCK_FOOTBALL_TEAM_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            logger.info(f"[MOCK] Retrieved football team stats for game {game_id}")
            return stats

        params = {"game_id": game_id}
        try:
            endpoint = self._get_endpoint_for_operation("team_stats")
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_team_stats_list(response)
            if not stats:
                raise ValueError(f"No team stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved football team stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch football team stats from API: {e}")
            raise

    async def get_player_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get player statistics for a football game."""
        if self.use_mock:
            stats = MOCK_FOOTBALL_PLAYER_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            logger.info(f"[MOCK] Retrieved football player stats for game {game_id}")
            return stats

        params = {"game_id": game_id}
        try:
            endpoint = self._get_endpoint_for_operation("player_stats")
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_player_stats_list(response)
            if not stats:
                raise ValueError(f"No player stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved football player stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch football player stats from API: {e}")
            raise
