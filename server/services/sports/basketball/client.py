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
    MOCK_BASKETBALL_LINEUP,
    MOCK_BASKETBALL_TEAM_RANK,
    MOCK_BASKETBALL_TEAM_VS_LIST,
)

logger = logging.getLogger(__name__)


class BasketballClient(BaseSportsClient):
    """Basketball Sports API client."""

    # League name -> League ID mapping
    LEAGUE_ID_MAP = {
        "NBA": "OT313",
        "KBL": "KBL",
        "WKBL": "WKBL",
    }

    # Team ID -> Display name mapping
    TEAM_NAME_MAP = {
        # NBA - Eastern Conference
        "OT31237": "클리블랜드", "OT31264": "인디애나", "OT31246": "보스턴",
        "OT31240": "올랜도", "OT31238": "밀워키", "OT31263": "뉴욕닉스",
        "OT31241": "디트로이트", "OT31265": "브루클린", "OT31266": "마이애미",
        "OT31267": "필라델피아", "OT31243": "시카고", "OT31239": "토론토",
        "OT31244": "애틀랜타", "OT31261": "샬렛", "OT31262": "워싱턴",
        # NBA - Western Conference
        "OT31255": "오클라호마시티", "OT31257": "멤피스", "OT31252": "휴스턴",
        "OT31254": "LA레이커스", "OT31250": "덴버", "OT31253": "LA클리퍼스",
        "OT31256": "미네소타", "OT31258": "피닉스", "OT31260": "골든스테이트",
        "OT31251": "댈러스", "OT31259": "새크라멘토", "OT31245": "샌안토니오",
        "OT31247": "포틀랜드", "OT31248": "유타", "OT31249": "뉴올리언스",
        # KBL
        "3LG": "창원LG", "3SK": "서울SK", "3KT": "수원KT", "3SS": "서울삼성",
        "3KG": "안양정관장", "3OR": "고양오리온", "3KA": "울산현대모비스",
        "3DB": "원주DB", "3HN": "대구한국가스공사", "3SN": "소노",
        # WKBL
        "3KB": "청주KB스타즈", "3HB": "하나원큐",
        "3BK": "BNK썸", "3SH": "신한은행", "3WB": "우리은행",
    }

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

    def get_league_id_map(self) -> Dict[str, str]:
        """Return basketball league name -> ID mapping."""
        return self.LEAGUE_ID_MAP

    def get_team_name_map(self) -> Dict[str, str]:
        """Return basketball team ID -> name mapping."""
        return self.TEAM_NAME_MAP

    def get_default_league(self) -> str:
        """Return default league for basketball."""
        return "NBA"

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

    async def get_lineup(self, game_id: str, team_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get lineup for a basketball team in a game.

        Args:
            game_id: Game ID
            team_id: Team ID

        Returns:
            List of players in lineup or None

        Raises:
            ValueError: Game or team not found
        """
        # Use mock data
        if self.use_mock:
            key = f"{game_id}_{team_id}"
            lineup = MOCK_BASKETBALL_LINEUP.get(key)

            if lineup is None:
                raise ValueError(f"Lineup not found for game {game_id}, team {team_id}")

            logger.info(f"[MOCK] Retrieved basketball lineup for game {game_id}, team {team_id}")
            return lineup

        # Call real API
        params = {
            "game_id": game_id,
            "team_id": team_id,
            "fmt": "json",
        }

        try:
            endpoint = self._get_endpoint_for_operation("lineup")
            response = await self._make_request(endpoint, params)
            lineup = self.mapper.map_lineup_list(response)

            if not lineup:
                raise ValueError(f"No lineup found for game {game_id}, team {team_id}")

            logger.info(f"[REAL API] Retrieved {len(lineup)} players in lineup for game {game_id}, team {team_id}")
            return lineup

        except Exception as e:
            logger.error(f"Failed to fetch basketball lineup from API: {e}")
            raise

    async def get_team_rank(self, season_id: str, league_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get team rankings for a basketball league/season.

        Args:
            season_id: Season ID (e.g., "2025")
            league_id: League ID (e.g., "OT313" for NBA)

        Returns:
            List of team rankings or None

        Raises:
            ValueError: Rankings not found
        """
        # Use mock data
        if self.use_mock:
            key = f"{season_id}_{league_id}"
            rankings = MOCK_BASKETBALL_TEAM_RANK.get(key)

            if rankings is None:
                raise ValueError(f"Rankings not found for season {season_id}, league {league_id}")

            logger.info(f"[MOCK] Retrieved basketball team rankings for season {season_id}, league {league_id}")
            return rankings

        # Call real API
        params = {
            "season_id": season_id,
            "league_id": league_id,
            "fmt": "json",
        }

        try:
            endpoint = self._get_endpoint_for_operation("team_rank")
            response = await self._make_request(endpoint, params)
            rankings = self.mapper.map_team_rank_list(response)

            if not rankings:
                raise ValueError(f"No rankings found for season {season_id}, league {league_id}")

            logger.info(f"[REAL API] Retrieved {len(rankings)} team rankings for season {season_id}, league {league_id}")
            return rankings

        except Exception as e:
            logger.error(f"Failed to fetch basketball team rankings from API: {e}")
            raise

    async def get_team_vs_list(
        self,
        season_id: str,
        league_id: str,
        game_id: str,
        home_team_id: str,
        away_team_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get team vs team comparison data for a basketball game.

        Args:
            season_id: Season ID (e.g., "2025")
            league_id: League ID (e.g., "OT313" for NBA)
            game_id: Game ID
            home_team_id: Home team ID
            away_team_id: Away team ID

        Returns:
            Team comparison data or None

        Raises:
            ValueError: Comparison data not found
        """
        # Use mock data
        if self.use_mock:
            data = MOCK_BASKETBALL_TEAM_VS_LIST.get(game_id)

            if data is None:
                logger.warning(f"[MOCK] Team vs list not found for game {game_id}")
                return None

            logger.info(f"[MOCK] Retrieved basketball team vs list for game {game_id}")
            return data

        # Call real API
        params = {
            "season_id": season_id,
            "league_id": league_id,
            "game_id": game_id,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "fmt": "json",
        }

        try:
            endpoint = self._get_endpoint_for_operation("team_vs_list")
            response = await self._make_request(endpoint, params)
            data = self.mapper.map_team_vs_list(response)

            if not data:
                logger.warning(f"[REAL API] No team vs list found for game {game_id}")
                return None

            logger.info(f"[REAL API] Retrieved basketball team vs list for game {game_id}")
            return data

        except Exception as e:
            logger.error(f"Failed to fetch basketball team vs list from API: {e}")
            raise
