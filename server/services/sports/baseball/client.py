"""Baseball-specific Sports API client."""
from typing import Dict, List, Any, Optional
import logging

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.baseball.mapper import BaseballMapper
from server.services.sports.baseball.endpoints import BASEBALL_ENDPOINTS
from server.services.sports.baseball.mock_data import (
    MOCK_BASEBALL_GAMES,
    MOCK_BASEBALL_GAME_TOTAL_INFO,
)
from server.services.leagues import load_league_config

logger = logging.getLogger(__name__)


class BaseballClient(BaseSportsClient):
    """Baseball Sports API client.

    Unlike other sports, baseball uses a single total_info endpoint
    that returns all game data (teams, innings, batters, pitchers, vs info).
    """

    def __init__(self):
        """Initialize baseball API client."""
        super().__init__()
        self._total_info_cache: Dict[str, Any] = {}
        self.mapper = BaseballMapper()

    def get_sport_name(self) -> str:
        """Return the sport name."""
        return "baseball"

    @property
    def endpoint_config(self):
        """Return baseball endpoint configuration."""
        return BASEBALL_ENDPOINTS

    def get_league_id_map(self) -> Dict[str, str]:
        """Return baseball league name -> ID mapping from config file."""
        return load_league_config("baseball")

    def get_default_league(self) -> str:
        """Return default league for baseball."""
        return "KBO리그"

    def get_status_map(self) -> Dict[str, str]:
        """Return baseball state code -> display status mapping.

        Baseball uses '경기전' instead of '예정'.
        """
        return {"F": "종료", "I": "진행중", "B": "경기전"}

    async def get_games_by_sport(self, date: str) -> List[Dict[str, Any]]:
        """Get baseball games for a specific date.

        Args:
            date: Date in YYYYMMDD format

        Returns:
            List of baseball games
        """
        if len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid date format: {date}. Must be YYYYMMDD")

        if self.use_mock:
            key = f"{date}_baseball"
            games = MOCK_BASEBALL_GAMES.get(key, [])
            logger.info(f"[MOCK] Retrieved {len(games)} baseball games for {date}")
            return games

        params = {
            "search_date": date,
            "compe": "baseball",
            "fmt": "json",
        }

        try:
            endpoint = self._get_endpoint_for_operation("games")
            response = await self._make_request(endpoint, params)
            games = self.mapper.map_games_list(response)
            logger.info(f"[REAL API] Retrieved {len(games)} baseball games for {date}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch baseball games from API: {e}")
            raise

    async def get_game_total_info(self, game_id: str) -> Dict[str, Any]:
        """Get all-in-one game data: teams, innings, batters, pitchers, vs info.

        This single API call returns all data needed for the game detail widget,
        unlike other sports which require multiple separate API calls.

        Args:
            game_id: Game ID

        Returns:
            Complete game data dict with gameInfo, homeTeamInfo, awayTeamInfo,
            totalStatInfo, inningScore, vsInfo, pitcherStat, batterStat

        Raises:
            ValueError: Game not found
        """
        if game_id in self._total_info_cache:
            logger.debug(f"[CACHE] Baseball total info cache hit for game {game_id}")
            return self._total_info_cache[game_id]

        if self.use_mock:
            data = MOCK_BASEBALL_GAME_TOTAL_INFO.get(game_id)
            if not data:
                raise ValueError(f"Baseball game {game_id} not found in mock data")
            logger.info(f"[MOCK] Retrieved baseball total info for game {game_id}")
            self._total_info_cache[game_id] = data
            return data

        params = {"game_id": game_id, "fmt": "json"}

        try:
            endpoint = self._get_endpoint_for_operation("total_info")
            response = await self._make_request(endpoint, params)
            logger.debug(f"[DEBUG] total_info raw response for {game_id}: {str(response)[:500]}")

            raw_data = response.get("Data", {})

            if isinstance(raw_data, dict):
                list_val = raw_data.get("list")
                if isinstance(list_val, list):
                    data = list_val[0] if list_val else {}
                elif isinstance(list_val, dict) and list_val:
                    data = list_val
                elif "gameInfo" in raw_data:
                    data = raw_data
                else:
                    data = {}
            elif isinstance(raw_data, list):
                data = raw_data[0] if raw_data else {}
            else:
                data = {}

            if not data:
                raise ValueError(f"No data returned for baseball game {game_id}")
            self._total_info_cache[game_id] = data
            logger.info(f"[REAL API] Retrieved baseball total info for game {game_id}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch baseball total info from API: {e}")
            raise
