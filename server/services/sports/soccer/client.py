"""Soccer-specific Sports API client."""
from typing import Dict, List, Any, Optional
import logging

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.soccer.mapper import SoccerMapper
from server.services.sports.soccer.endpoints import SOCCER_ENDPOINTS
from server.services.sports.soccer.mock_data import (
    MOCK_SOCCER_GAMES,
    MOCK_SOCCER_TEAM_STATS,
    MOCK_SOCCER_PLAYER_STATS,
    MOCK_SOCCER_LINEUP,
    MOCK_SOCCER_PLAYER_SEASON_STATS,
    MOCK_SOCCER_TEAM_RANK,
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

    @property
    def endpoint_config(self):
        """Return soccer endpoint configuration."""
        return SOCCER_ENDPOINTS

    async def get_games_by_sport(self, date: str) -> List[Dict[str, Any]]:
        """Get soccer games for a specific date."""
        if len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid date format: {date}. Must be YYYYMMDD")

        if self.use_mock:
            key = f"{date}_soccer"
            games = MOCK_SOCCER_GAMES.get(key, [])
            logger.info(f"[MOCK] Retrieved {len(games)} soccer games for {date}")
            return games

        params = {
            "search_date": date,
            "compe": "soccer",
            "fmt": "json",
        }
        try:
            endpoint = self._get_endpoint_for_operation("games")
            response = await self._make_request(endpoint, params)
            games = self.mapper.map_games_list(response)
            logger.info(f"[REAL API] Retrieved {len(games)} soccer games for {date}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch soccer games from API: {e}")
            raise

    async def get_team_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get team statistics for a soccer game."""
        if self.use_mock:
            stats = MOCK_SOCCER_TEAM_STATS.get(game_id)
            if stats is None:
                raise ValueError(f"Game {game_id} not found")
            # Apply same mapping as real API for consistency
            mapped_stats = self.mapper.map_team_stats_list(stats)
            logger.info(f"[MOCK] Retrieved soccer team stats for game {game_id}")
            return mapped_stats

        params = {"game_id": game_id}
        try:
            endpoint = self._get_endpoint_for_operation("team_stats")
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_team_stats_list(response)
            if not stats:
                raise ValueError(f"No team stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved soccer team stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch soccer team stats from API: {e}")
            raise

    async def get_player_stats(self, game_id: str) -> Optional[List[Dict[str, Any]]]:
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
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_player_stats_list(response)
            if not stats:
                raise ValueError(f"No player stats found for game {game_id}")
            logger.info(f"[REAL API] Retrieved soccer player stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch soccer player stats from API: {e}")
            raise

    async def get_lineup(self, game_id: str, team_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get lineup for a soccer team in a game.

        Args:
            game_id: Game ID
            team_id: Team ID

        Returns:
            List of players in lineup or None

        Raises:
            ValueError: Game or team not found
        """
        if self.use_mock:
            key = f"{game_id}_{team_id}"
            lineup = MOCK_SOCCER_LINEUP.get(key)
            if lineup is None:
                raise ValueError(f"Lineup not found for game {game_id}, team {team_id}")
            logger.info(f"[MOCK] Retrieved soccer lineup for game {game_id}, team {team_id}")
            return lineup

        params = {"game_id": game_id, "team_id": team_id, "fmt": "json"}
        try:
            endpoint = self._get_endpoint_for_operation("lineup")
            response = await self._make_request(endpoint, params)
            lineup = self.mapper.map_lineup_list(response)
            if not lineup:
                raise ValueError(f"No lineup found for game {game_id}, team {team_id}")
            logger.info(f"[REAL API] Retrieved {len(lineup)} players in lineup for game {game_id}, team {team_id}")
            return lineup
        except Exception as e:
            logger.error(f"Failed to fetch soccer lineup from API: {e}")
            raise

    async def get_player_season_stats(
        self,
        league_id: str,
        season_id: str,
        team_id: str,
        player_id: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get player season statistics.

        Args:
            league_id: League ID (e.g., 'OT22187')
            season_id: Season ID (e.g., '2025')
            team_id: Team ID (e.g., 'OT22253')
            player_id: Player ID (e.g., 'OT253039')

        Returns:
            List of player season stats or None

        Raises:
            ValueError: Player season stats not found
        """
        if self.use_mock:
            key = f"{league_id}_{season_id}_{team_id}_{player_id}"
            stats = MOCK_SOCCER_PLAYER_SEASON_STATS.get(key)
            if stats is None:
                raise ValueError(
                    f"Player season stats not found for league={league_id}, "
                    f"season={season_id}, team={team_id}, player={player_id}"
                )
            logger.info(
                f"[MOCK] Retrieved player season stats for player {player_id} "
                f"(team={team_id}, league={league_id}, season={season_id})"
            )
            return stats

        params = {
            "league_id": league_id,
            "season_id": season_id,
            "team_id": team_id,
            "player_id": player_id,
            "fmt": "json",
        }
        try:
            endpoint = self._get_endpoint_for_operation("player_season_stats")
            response = await self._make_request(endpoint, params)
            stats = self.mapper.map_player_season_stats(response)
            if not stats:
                raise ValueError(
                    f"No player season stats found for league={league_id}, "
                    f"season={season_id}, team={team_id}, player={player_id}"
                )
            logger.info(
                f"[REAL API] Retrieved player season stats for player {player_id} "
                f"(team={team_id}, league={league_id}, season={season_id})"
            )
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch player season stats from API: {e}")
            raise

    async def get_team_rank(
        self,
        season_id: str,
        league_id: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get team rankings (league standings) for a league.

        Args:
            season_id: Season ID (e.g., '2025')
            league_id: League ID (e.g., 'OT22187')

        Returns:
            List of team rankings or None

        Raises:
            ValueError: Team rankings not found
        """
        if self.use_mock:
            key = f"{league_id}_{season_id}"
            rankings = MOCK_SOCCER_TEAM_RANK.get(key)
            if rankings is None:
                logger.warning(
                    f"[MOCK] Team rankings not found for league={league_id}, season={season_id}"
                )
                return []
            logger.info(
                f"[MOCK] Retrieved {len(rankings)} team rankings for "
                f"league={league_id}, season={season_id}"
            )
            return self.mapper.map_team_rank_list({"Data": {"list": rankings}})

        params = {
            "league_id": league_id,
            "season_id": season_id,
            "fmt": "json",
        }
        try:
            endpoint = self._get_endpoint_for_operation("team_rank")
            response = await self._make_request(endpoint, params)
            rankings = self.mapper.map_team_rank_list(response)
            logger.info(
                f"[REAL API] Retrieved {len(rankings)} team rankings for "
                f"league={league_id}, season={season_id}"
            )
            return rankings
        except Exception as e:
            logger.error(f"Failed to fetch team rankings from API: {e}")
            raise
