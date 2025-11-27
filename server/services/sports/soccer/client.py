"""Soccer-specific Sports API client."""
from typing import Dict, List, Any, Optional
import logging

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.soccer.mapper import SoccerMapper
from server.services.sports.soccer.mock_data import (
    MOCK_SOCCER_GAMES,
    MOCK_SOCCER_TEAM_STATS,
    MOCK_SOCCER_PLAYER_STATS,
)

logger = logging.getLogger(__name__)


class SoccerClient(BaseSportsClient):
    """Soccer Sports API client."""

    def __init__(self):
        """Initialize soccer API client."""
        super().__init__()
        self.mapper = SoccerMapper()

    def get_sport_name(self) -> str:
        """Return the sport name."""
        return "soccer"

    def get_games_by_sport(self, date: str) -> List[Dict[str, Any]]:
        """Get soccer games for a specific date."""
        if len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid date format: {date}. Must be YYYYMMDD")

        if self.use_mock:
            key = f"{date}_soccer"
            games = MOCK_SOCCER_GAMES.get(key, [])
            logger.info(f"[MOCK] Retrieved {len(games)} soccer games for {date}")
            return games

        params = {"date": date, "sport": "soccer"}
        try:
            endpoint = self._get_endpoint_for_operation("games")
            response = self._make_request(endpoint, params)
            games = self.mapper.map_games_list(response)
            logger.info(f"[REAL API] Retrieved {len(games)} soccer games for {date}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch soccer games from API: {e}")
            raise

    def get_team_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get team statistics for a soccer game."""
        if self.use_mock:
            stats = MOCK_SOCCER_TEAM_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            logger.info(f"[MOCK] Retrieved soccer team stats for game {game_id}")
            return stats

        params = {"game_id": game_id}
        try:
            endpoint = self._get_endpoint_for_operation("team_stats")
            response = self._make_request(endpoint, params)
            stats = self.mapper.map_team_stats_list(response)
            if not stats:
                raise ValueError(f"No team stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved soccer team stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch soccer team stats from API: {e}")
            raise

    def get_player_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get player statistics for a soccer game."""
        if self.use_mock:
            stats = MOCK_SOCCER_PLAYER_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            logger.info(f"[MOCK] Retrieved soccer player stats for game {game_id}")
            return stats

        params = {"game_id": game_id}
        try:
            endpoint = self._get_endpoint_for_operation("player_stats")
            response = self._make_request(endpoint, params)
            stats = self.mapper.map_player_stats_list(response)
            if not stats:
                raise ValueError(f"No player stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved soccer player stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch soccer player stats from API: {e}")
            raise
