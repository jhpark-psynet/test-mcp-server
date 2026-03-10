"""Volleyball-specific Sports API client."""
from typing import Dict, List, Any, Optional, Tuple
import logging

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.volleyball.mapper import VolleyballMapper
from server.services.sports.volleyball.endpoints import VOLLEYBALL_ENDPOINTS
from server.services.sports.volleyball.mock_data import (
    MOCK_VOLLEYBALL_GAMES,
    MOCK_VOLLEYBALL_TEAM_STATS,
    MOCK_VOLLEYBALL_PLAYER_STATS,
)
from server.services.leagues import load_league_config

logger = logging.getLogger(__name__)


class VolleyballClient(BaseSportsClient):
    """Volleyball Sports API client."""

    # V리그 team colors {team_id: (primary_hex, secondary_hex)}
    # 실제 API 응답 확인 후 팀 ID별 색상 추가 가능
    TEAM_COLORS: Dict[str, Tuple[str, str]] = {}

    DEFAULT_COLORS: Tuple[str, str] = ("#003DA5", "#FFFFFF")

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

    # League ID → display name (from leagueList API, confirmed values)
    LEAGUE_ID_TO_DISPLAY: Dict[str, str] = {
        "41": "V리그남자",
        "42": "V리그여자",
        "EB911961": "V리그남자",
        "EB911962": "V리그여자",
        "EB9110264": "VNL여자",
        "EB9110458": "VNL남자",
    }

    # Fallback: API league name → display name (when league_id is unavailable)
    LEAGUE_DISPLAY_MAP: Dict[str, str] = {
        "V-리그": "V리그남자",
        "V-리그 (여)": "V리그여자",
        "V리그": "V리그남자",
        "V리그 (여)": "V리그여자",
        "V리그남자": "V리그남자",
        "V리그여자": "V리그여자",
        "VNL남자": "VNL남자",
        "VNL여자": "VNL여자",
    }

    def get_league_id_map(self) -> Dict[str, str]:
        """Return volleyball league name -> ID mapping from config file."""
        return load_league_config("volleyball")

    def normalize_league_name(self, league_name: str, league_id: str = "") -> str:
        """Normalize API league name to a schema-compatible display name.

        Uses league_id for precise men's/women's distinction when available.
        Falls back to league_name mapping.
        """
        if league_id and league_id in self.LEAGUE_ID_TO_DISPLAY:
            return self.LEAGUE_ID_TO_DISPLAY[league_id]
        return self.LEAGUE_DISPLAY_MAP.get(league_name, league_name)

    def get_status_map(self) -> Dict[str, str]:
        """Return volleyball-specific status mapping."""
        return {"F": "종료", "I": "진행중", "B": "예정"}

    def get_extra_team_fields(self, team_id: str, score: int) -> Dict[str, Any]:
        """Return volleyball-specific extra team fields (setsWon, colors)."""
        primary, secondary = self.TEAM_COLORS.get(team_id, self.DEFAULT_COLORS)
        return {
            "setsWon": score,
            "primaryColor": primary,
            "secondaryColor": secondary,
        }

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

    async def get_player_stats(
        self,
        game_id: str,
        home_team_id: str = "",
        away_team_id: str = "",
    ) -> Optional[List[Dict[str, Any]]]:
        """Get player statistics for a volleyball game.

        Volleyball API requires team_id per request, so we call the endpoint
        once per team and combine the results.
        """
        if self.use_mock:
            stats = MOCK_VOLLEYBALL_PLAYER_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            logger.info(f"[MOCK] Retrieved volleyball player stats for game {game_id}")
            return stats

        endpoint = self._get_endpoint_for_operation("player_stats")
        all_stats: List[Dict[str, Any]] = []

        for team_id in [home_team_id, away_team_id]:
            if not team_id:
                continue
            try:
                response = await self._make_request(endpoint, {"game_id": game_id, "team_id": team_id})
                if logger.isEnabledFor(logging.DEBUG):
                    raw_items = response.get("Data", {}).get("list", [])
                    if raw_items:
                        logger.debug(f"[DEBUG] volleyball player stat raw keys: {list(raw_items[0].keys())}")
                        logger.debug(f"[DEBUG] volleyball player stat first record: {raw_items[0]}")
                team_stats = self.mapper.map_player_stats_list(response)
                all_stats.extend(team_stats)
                logger.debug(f"[REAL API] {len(team_stats)} players for team {team_id}")
            except Exception as e:
                logger.warning(f"Failed to fetch player stats for team {team_id}: {e}")

        if not all_stats:
            raise ValueError(f"No player stats found for game {game_id}")

        logger.info(f"[REAL API] Retrieved {len(all_stats)} volleyball player stats for game {game_id}")
        return all_stats
