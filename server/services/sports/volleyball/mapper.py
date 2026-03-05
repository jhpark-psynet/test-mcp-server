"""Volleyball-specific response mapper."""
from typing import Any, Dict, List, Union
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
        """Return field mapping for volleyball team stats.

        Volleyball team stats API returns a single combined record with
        home_team_* and away_team_* prefixed fields.
        No mapping needed (fields are already lowercase).
        """
        return {}

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for volleyball player stats.

        Volleyball player stats API returns lowercase field names directly.
        No mapping needed.
        """
        return {}

    def map_team_stats_list(self, api_response: Any) -> List[Dict[str, Any]]:
        """Override: volleyball API returns a single combined home+away record.

        Returns the single record duplicated as [combined, combined] so that
        the handler's has_team_stats check (len >= 2) passes, and both
        home_stats and away_stats receive the same combined record.
        """
        if isinstance(api_response, dict) and "Data" in api_response:
            data = api_response["Data"]
            if isinstance(data, dict) and "list" in data:
                items = data["list"]
                if items:
                    return [items[0], items[0]]
        return []

    def build_game_records(
        self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build volleyball-specific game records for display.

        Both home_stats and away_stats are the same combined record
        (from map_team_stats_list override), so we read home_team_* and
        away_team_* prefixed fields from the same dict.

        Args:
            home_stats: Combined team stats record (home_team_* + away_team_* fields)
            away_stats: Same combined record (unused; home_stats used for all reads)

        Returns:
            List of game record dicts with volleyball stats
        """
        s = home_stats  # combined record

        home_atk_s = _safe_int(s.get("home_team_atk_success_cn"), 0)
        home_atk_t = _safe_int(s.get("home_team_atk_try_cn"), 1)
        away_atk_s = _safe_int(s.get("away_team_atk_success_cn"), 0)
        away_atk_t = _safe_int(s.get("away_team_atk_try_cn"), 1)

        return [
            {
                "label": "공격(성공/시도)",
                "home": f"{home_atk_s}/{home_atk_t}",
                "away": f"{away_atk_s}/{away_atk_t}",
            },
            {
                "label": "공격 블록당함",
                "home": _safe_int(s.get("home_team_atk_block_cn"), 0),
                "away": _safe_int(s.get("away_team_atk_block_cn"), 0),
            },
            {
                "label": "공격 범실",
                "home": _safe_int(s.get("home_team_atk_err_cn"), 0),
                "away": _safe_int(s.get("away_team_atk_err_cn"), 0),
            },
            {
                "label": "블로킹",
                "home": _safe_int(s.get("home_team_block_success_cn"), 0),
                "away": _safe_int(s.get("away_team_block_success_cn"), 0),
            },
            {
                "label": "서브(성공/시도)",
                "home": f"{_safe_int(s.get('home_team_srv_success_cn'), 0)}/{_safe_int(s.get('home_team_srv_try_cn'), 0)}",
                "away": f"{_safe_int(s.get('away_team_srv_success_cn'), 0)}/{_safe_int(s.get('away_team_srv_try_cn'), 0)}",
            },
            {
                "label": "서브 범실",
                "home": _safe_int(s.get("home_team_srv_err_cn"), 0),
                "away": _safe_int(s.get("away_team_srv_err_cn"), 0),
            },
            {
                "label": "세트(성공/시도)",
                "home": f"{_safe_int(s.get('home_team_set_success_cn'), 0)}/{_safe_int(s.get('home_team_set_try_cn'), 0)}",
                "away": f"{_safe_int(s.get('away_team_set_success_cn'), 0)}/{_safe_int(s.get('away_team_set_try_cn'), 0)}",
            },
            {
                "label": "디그(성공/시도)",
                "home": f"{_safe_int(s.get('home_team_dig_success_cn'), 0)}/{_safe_int(s.get('home_team_dig_try_cn'), 0)}",
                "away": f"{_safe_int(s.get('away_team_dig_success_cn'), 0)}/{_safe_int(s.get('away_team_dig_try_cn'), 0)}",
            },
            {
                "label": "리시브(성공/시도)",
                "home": f"{_safe_int(s.get('home_team_rcv_exact_cn'), 0)}/{_safe_int(s.get('home_team_rcv_try_cn'), 0)}",
                "away": f"{_safe_int(s.get('away_team_rcv_exact_cn'), 0)}/{_safe_int(s.get('away_team_rcv_try_cn'), 0)}",
            },
            {
                "label": "리시브 실패",
                "home": _safe_int(s.get("home_team_rcv_fail_cn"), 0),
                "away": _safe_int(s.get("away_team_rcv_fail_cn"), 0),
            },
        ]
