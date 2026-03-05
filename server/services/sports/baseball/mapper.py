"""Baseball-specific response mapper."""
from typing import Any, Dict, List, Union
from server.services.sports.base.mapper import BaseResponseMapper


def _format_rate(value: Any, decimals: int = 3) -> str:
    """Format a float rate value to fixed decimal places."""
    if value is None:
        return "0." + "0" * decimals
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


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


class BaseballMapper(BaseResponseMapper):
    """Response mapper for Baseball API."""

    def get_game_field_map(self) -> Dict[str, str]:
        """Return field mapping for baseball games list."""
        return {
            "GAME_ID": "game_id",
            "LEAGUE_ID": "league_id",
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
        """Baseball uses single total_info API, no separate team stats mapping needed."""
        return {}

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Baseball uses single total_info API, no separate player stats mapping needed."""
        return {}

    def build_game_records(
        self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build baseball game records from totalStatInfo.

        Both home_stats and away_stats are the same totalStatInfo dict
        (contains home_team_* and away_team_* fields).
        """
        stat = home_stats  # combined record with both home_team_* and away_team_* fields
        return [
            {
                "label": "안타",
                "home": _safe_int(stat.get("home_team_hit_cn")),
                "away": _safe_int(stat.get("away_team_hit_cn")),
            },
            {
                "label": "홈런",
                "home": _safe_int(stat.get("home_team_hr_cn")),
                "away": _safe_int(stat.get("away_team_hr_cn")),
            },
            {
                "label": "볼넷/사구",
                "home": _safe_int(stat.get("home_team_bbhp_cn")),
                "away": _safe_int(stat.get("away_team_bbhp_cn")),
            },
            {
                "label": "도루",
                "home": _safe_int(stat.get("home_team_sb_cn")),
                "away": _safe_int(stat.get("away_team_sb_cn")),
            },
            {
                "label": "실책",
                "home": _safe_int(stat.get("home_team_err_cn")),
                "away": _safe_int(stat.get("away_team_err_cn")),
            },
            {
                "label": "팀타율",
                "home": _format_rate(stat.get("home_team_h_hra"), 3),
                "away": _format_rate(stat.get("away_team_h_hra"), 3),
            },
            {
                "label": "팀ERA",
                "home": _format_rate(stat.get("home_team_p_era"), 2),
                "away": _format_rate(stat.get("away_team_p_era"), 2),
            },
        ]
