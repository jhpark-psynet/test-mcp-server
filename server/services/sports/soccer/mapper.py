"""Soccer-specific response mapper."""
from typing import Dict, List, Any, Union
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
