"""Soccer-specific response mapper."""
from typing import Dict, List, Any, Union, Set
from server.services.sports.base.mapper import BaseResponseMapper


def _safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """Safely convert to int."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    return default


class SoccerMapper(BaseResponseMapper):
    """Response mapper for Soccer API."""

    # Position code -> display name mapping
    POSITION_MAP: Dict[str, str] = {
        "1": "GK",       # 골키퍼
        "2": "DF",       # 수비
        "3": "MF",       # 미드필더
        "4": "FW",       # 공격수
        "5": "BENCH",    # 벤치
        "14": "STARTER", # 선발 (포지션 미지정)
    }

    # Starter position codes
    STARTER_POSITIONS: Set[str] = {"1", "2", "3", "4", "14"}

    def get_game_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer games list."""
        return {
            "GAME_ID": "game_id",
            "LEAGUE_NAME": "league_name",
            "MATCH_DATE": "match_date",
            "MATCH_TIME": "match_time",
            "HOME_TEAM_ID": "home_team_id",
            "AWAY_TEAM_ID": "away_team_id",
            "HOME_TEAM_NAME": "home_team_name",
            "AWAY_TEAM_NAME": "away_team_name",
            "HOME_SCORE": "home_score",
            "AWAY_SCORE": "away_score",
            "STATE": "state",
            "ARENA_NAME": "arena_name",
            "COMPE": "compe",
        }

    def get_team_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer team stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer player stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}

    def build_game_records(
        self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build soccer-specific game records for display.

        Args:
            home_stats: Home team statistics
            away_stats: Away team statistics

        Returns:
            List of game record dicts with soccer stats
        """
        # Note: Field names may need adjustment based on actual API response
        return [
            {
                "label": "슈팅",
                "home": _safe_int(home_stats.get("home_team_shots_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_shots_cn"), 0),
            },
            {
                "label": "유효슈팅",
                "home": _safe_int(home_stats.get("home_team_shots_on_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_shots_on_cn"), 0),
            },
            {
                "label": "점유율",
                "home": f"{_safe_int(home_stats.get('home_team_possession_rt'), 50)}%",
                "away": f"{_safe_int(away_stats.get('away_team_possession_rt'), 50)}%",
            },
            {
                "label": "패스",
                "home": _safe_int(home_stats.get("home_team_pass_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_pass_cn"), 0),
            },
            {
                "label": "파울",
                "home": _safe_int(home_stats.get("home_team_foul_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_foul_cn"), 0),
            },
            {
                "label": "코너킥",
                "home": _safe_int(home_stats.get("home_team_corner_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_corner_cn"), 0),
            },
            {
                "label": "오프사이드",
                "home": _safe_int(home_stats.get("home_team_offside_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_offside_cn"), 0),
            },
            {
                "label": "옐로카드",
                "home": _safe_int(home_stats.get("home_team_yellow_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_yellow_cn"), 0),
            },
        ]

    def get_position_map(self) -> Dict[str, str]:
        """Return soccer position map."""
        return self.POSITION_MAP

    def get_starter_positions(self) -> Set[str]:
        """Return soccer starter position codes."""
        return self.STARTER_POSITIONS

    def get_lineup_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer lineup."""
        return {
            "PLAYER_ID": "player_id",
            "PLAYER_NAME": "player_name",
            "BACK_NO": "back_no",
            "POS_NO": "pos_no",
            "GOAL_CN": "goal_cn",
            "RATING": "rating",
        }

    def map_lineup_list(self, response: Any) -> List[Dict[str, Any]]:
        """Map lineup API response to standardized format."""
        data = response.get("Data", {})
        items = data.get("list", [])
        field_map = self.get_lineup_field_map()
        return [self._apply_field_mapping(item, field_map) for item in items]
