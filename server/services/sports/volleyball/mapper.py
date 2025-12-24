"""Volleyball-specific response mapper."""
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


class VolleyballMapper(BaseResponseMapper):
    """Response mapper for Volleyball API."""

    def get_game_field_map(self) -> Dict[str, str]:
        """Return field mapping for volleyball games list."""
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
        """Return field mapping for volleyball team stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for volleyball player stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}

    def build_game_records(
        self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build volleyball-specific game records for display.

        Args:
            home_stats: Home team statistics
            away_stats: Away team statistics

        Returns:
            List of game record dicts with volleyball stats
        """
        # Note: Field names may need adjustment based on actual API response
        return [
            {
                "label": "공격성공",
                "home": _safe_int(home_stats.get("home_team_attack_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_attack_cn"), 0),
            },
            {
                "label": "공격시도",
                "home": _safe_int(home_stats.get("home_team_attack_try_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_attack_try_cn"), 0),
            },
            {
                "label": "블로킹",
                "home": _safe_int(home_stats.get("home_team_block_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_block_cn"), 0),
            },
            {
                "label": "서브에이스",
                "home": _safe_int(home_stats.get("home_team_serve_ace_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_serve_ace_cn"), 0),
            },
            {
                "label": "서브실패",
                "home": _safe_int(home_stats.get("home_team_serve_error_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_serve_error_cn"), 0),
            },
            {
                "label": "디그",
                "home": _safe_int(home_stats.get("home_team_dig_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_dig_cn"), 0),
            },
            {
                "label": "실점",
                "home": _safe_int(home_stats.get("home_team_error_cn"), 0),
                "away": _safe_int(away_stats.get("away_team_error_cn"), 0),
            },
        ]
