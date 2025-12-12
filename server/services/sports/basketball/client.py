"""Basketball-specific Sports API client."""
from typing import Dict, List, Any, Optional
import logging

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.basketball.mapper import BasketballMapper
from server.services.sports.basketball.endpoints import BASKETBALL_ENDPOINTS
from server.services.sports.basketball.mock_data import (
    MOCK_BASKETBALL_GAMES,
    MOCK_BASKETBALL_TEAM_STATS,
    MOCK_BASKETBALL_PLAYER_STATS,
)

logger = logging.getLogger(__name__)


class BasketballClient(BaseSportsClient):
    """Basketball Sports API client."""

    def __init__(self):
        """Initialize basketball API client."""
        super().__init__()
        self.mapper = BasketballMapper()

    def get_sport_name(self) -> str:
        """Return the sport name."""
        return "basketball"

    @property
    def endpoint_config(self):
        """Return basketball endpoint configuration."""
        return BASKETBALL_ENDPOINTS

    async def get_games_by_sport(self, date: str) -> List[Dict[str, Any]]:
        """Get basketball games for a specific date.

        Args:
            date: Date in YYYYMMDD format

        Returns:
            List of basketball games

        Raises:
            ValueError: Invalid date format
        """
        if len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid date format: {date}. Must be YYYYMMDD")

        # Use mock data
        if self.use_mock:
            key = f"{date}_basketball"
            games = MOCK_BASKETBALL_GAMES.get(key, [])
            logger.info(f"[MOCK] Retrieved {len(games)} basketball games for {date}")
            return games

        # Call real API
        params = {
            "search_date": date,
            "compe": "basketball",
            "fmt": "json",
        }

        try:
            endpoint = self._get_endpoint_for_operation("games")
            response = await self._make_request(endpoint, params)
            games = self.mapper.map_games_list(response)
            logger.info(f"[REAL API] Retrieved {len(games)} basketball games for {date}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch basketball games from API: {e}")
            raise

    async def get_team_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get team statistics for a basketball game.

        Args:
            game_id: Game ID

        Returns:
            List of team stats [home_team, away_team] or None

        Raises:
            ValueError: Game not found or not started yet
        """
        # Use mock data
        if self.use_mock:
            stats = MOCK_BASKETBALL_TEAM_STATS.get(game_id)

            if stats is None:
                # Check if game exists but hasn't started
                for games in MOCK_BASKETBALL_GAMES.values():
                    for game in games:
                        if game["game_id"] == game_id:
                            if game["state"] == "b":
                                raise ValueError(
                                    f"Game {game_id} has not started yet. Team stats not available."
                                )
                            break

                raise ValueError(f"Game {game_id} not found")

            logger.info(f"[MOCK] Retrieved basketball team stats for game {game_id}")
            return stats

        # Call real API
        params = {
            "game_id": game_id,
            "fmt": "json",
        }

        try:
            endpoint = self._get_endpoint_for_operation("team_stats")
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_team_stats_list(response)

            if not stats:
                raise ValueError(f"No team stats found for game {game_id}")

            logger.info(f"[REAL API] Retrieved basketball team stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch basketball team stats from API: {e}")
            raise

    async def get_player_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get player statistics for a basketball game.

        Args:
            game_id: Game ID

        Returns:
            List of player stats or None

        Raises:
            ValueError: Game not found or not started yet
        """
        # Use mock data
        if self.use_mock:
            stats = MOCK_BASKETBALL_PLAYER_STATS.get(game_id)

            if stats is None:
                # Check if game exists but hasn't started
                for games in MOCK_BASKETBALL_GAMES.values():
                    for game in games:
                        if game["game_id"] == game_id:
                            if game["state"] == "b":
                                raise ValueError(
                                    f"Game {game_id} has not started yet. Player stats not available."
                                )
                            break

                raise ValueError(f"Game {game_id} not found")

            logger.info(f"[MOCK] Retrieved basketball player stats for game {game_id}")
            return stats

        # Call real API - Player stats requires team_id
        # First get team IDs from team stats
        try:
            team_stats = await self.get_team_stats(game_id)
            if not team_stats or len(team_stats) < 2:
                raise ValueError(f"Could not get team IDs for game {game_id}")

            # Extract team IDs
            home_team_id = team_stats[0].get("home_team_id")
            away_team_id = team_stats[1].get("away_team_id")

            if not home_team_id or not away_team_id:
                raise ValueError(f"Team IDs not found in team stats for game {game_id}")

            logger.debug(f"Fetching player stats for teams: {home_team_id}, {away_team_id}")

            # Fetch player stats for both teams
            endpoint = self._get_endpoint_for_operation("player_stats")
            all_player_stats = []

            for team_id in [home_team_id, away_team_id]:
                params = {
                    "game_id": game_id,
                    "team_id": team_id,
                    "fmt": "json",
                }

                response = await self._make_request(endpoint, params)
                team_players = self.mapper.map_player_stats_list(response)
                all_player_stats.extend(team_players)

            if not all_player_stats:
                raise ValueError(f"No player stats found for game {game_id}")

            logger.info(
                f"[REAL API] Retrieved {len(all_player_stats)} basketball player stats for game {game_id}"
            )
            return all_player_stats

        except Exception as e:
            logger.error(f"Failed to fetch basketball player stats from API: {e}")
            raise
