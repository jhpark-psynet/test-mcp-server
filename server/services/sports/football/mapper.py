"""Football (American) specific response mapper."""
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


class FootballMapper(BaseResponseMapper):
    """Response mapper for Football (American) API."""

    def get_game_field_map(self) -> Dict[str, str]:
        """Return field mapping for football games list."""
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
        """Return field mapping for football team stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for football player stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}

    def build_game_records(
        self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build football-specific game records for display.

        Args:
            home_stats: Home team statistics
            away_stats: Away team statistics

        Returns:
            List of game record dicts with football stats
        """
        # Note: Field names may need adjustment based on actual API response
        return [
            {
                "label": "총야드",
                "home": _safe_int(home_stats.get("home_team_total_yards"), 0),
                "away": _safe_int(away_stats.get("away_team_total_yards"), 0),
            },
            {
                "label": "패싱야드",
                "home": _safe_int(home_stats.get("home_team_passing_yards"), 0),
                "away": _safe_int(away_stats.get("away_team_passing_yards"), 0),
            },
            {
                "label": "러싱야드",
                "home": _safe_int(home_stats.get("home_team_rushing_yards"), 0),
                "away": _safe_int(away_stats.get("away_team_rushing_yards"), 0),
            },
            {
                "label": "1st다운",
                "home": _safe_int(home_stats.get("home_team_first_downs"), 0),
                "away": _safe_int(away_stats.get("away_team_first_downs"), 0),
            },
            {
                "label": "터노버",
                "home": _safe_int(home_stats.get("home_team_turnovers"), 0),
                "away": _safe_int(away_stats.get("away_team_turnovers"), 0),
            },
            {
                "label": "새크",
                "home": _safe_int(home_stats.get("home_team_sacks"), 0),
                "away": _safe_int(away_stats.get("away_team_sacks"), 0),
            },
            {
                "label": "점유시간",
                "home": home_stats.get("home_team_possession", "00:00"),
                "away": away_stats.get("away_team_possession", "00:00"),
            },
        ]
