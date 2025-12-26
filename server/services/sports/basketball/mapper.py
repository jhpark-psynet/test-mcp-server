"""Basketball-specific response mapper."""
from typing import Dict, List, Any, Union, Set
from server.services.sports.base.mapper import BaseResponseMapper


def _safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """Safely convert to int. Handles empty string, None, whitespace."""
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


class BasketballMapper(BaseResponseMapper):
    """Response mapper for Basketball API."""

    # Position code -> display name mapping
    POSITION_MAP = {
        "21": "C",    # 센터
        "22": "PF",   # 파워포워드
        "23": "SF",   # 스몰포워드
        "24": "PG",   # 포인트가드
        "25": "SG",   # 슈팅가드
        "5": "BENCH", # 벤치
    }

    # Starter position codes
    STARTER_POSITIONS: Set[str] = {"21", "22", "23", "24", "25"}

    def get_game_field_map(self) -> Dict[str, str]:
        """Return field mapping for basketball games list."""
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
        """Return field mapping for basketball team stats.

        Note: Basketball Team Stats API already returns lowercase field names
        (e.g., home_team_id, home_team_fgm_cn), so no field mapping is needed.
        Returning empty dict means the original field names will be used as-is.
        """
        return {}

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for basketball player stats.

        Note: Basketball Player Stats API already returns lowercase field names
        (e.g., game_id, player_name, tot_score), so no field mapping is needed.
        Returning empty dict means the original field names will be used as-is.
        """
        return {}

    def get_lineup_field_map(self) -> Dict[str, str]:
        """Return field mapping for basketball lineup."""
        return {
            "PLAYER_ID": "player_id",
            "PLAYER_NAME": "player_name",
            "BACK_NO": "back_no",
            "POS_NO": "pos_no",
        }

    def map_lineup_list(self, response: Any) -> List[Dict[str, Any]]:
        """Map lineup API response to standardized format.

        Args:
            response: Raw API response

        Returns:
            List of lineup entries with mapped field names
        """
        data = response.get("Data", {})
        items = data.get("list", [])

        field_map = self.get_lineup_field_map()
        return [self._apply_field_mapping(item, field_map) for item in items]

    def get_team_rank_field_map(self) -> Dict[str, str]:
        """Return field mapping for basketball team rankings."""
        return {
            "group_sc": "group",
            "rank": "rank",
            "team_id": "team_id",
            "team_name": "team_name",
            "game_cn": "games",
            "all_w_cn": "wins",
            "all_l_cn": "losses",
            "all_wra_rt": "win_rate",
            "all_wingap_va": "games_behind",
            "all_r_score": "points_per_game",
            "all_l_score": "points_against",
            "all_fgp_rt": "field_goal_pct",
            "all_p3_rt": "three_point_pct",
            "all_fpt_rt": "free_throw_pct",
            "all_reb_cn": "rebounds",
            "all_assist_cn": "assists",
            "all_turnover_cn": "turnovers",
            "all_steal_cn": "steals",
        }

    def map_team_rank_list(self, response: Any) -> List[Dict[str, Any]]:
        """Map team rank API response to standardized format.

        Args:
            response: Raw API response

        Returns:
            List of team rankings with mapped field names
        """
        data = response.get("Data", {})
        items = data.get("list", [])

        field_map = self.get_team_rank_field_map()
        return [self._apply_field_mapping(item, field_map) for item in items]

    def get_team_vs_list_field_map(self) -> Dict[str, str]:
        """Return field mapping for basketball team vs team comparison."""
        return {
            # IDs
            "season_id": "season_id",
            "league_id": "league_id",
            "game_id": "game_id",
            "home_team_id": "home_team_id",
            "away_team_id": "away_team_id",
            # Conference and rank
            "home_group_sc": "home_conference",
            "away_group_sc": "away_conference",
            "home_team_rank": "home_rank",
            "away_team_rank": "away_rank",
            # Season record
            "home_team_all_w_cn": "home_wins",
            "away_team_all_w_cn": "away_wins",
            "home_team_all_l_cn": "home_losses",
            "away_team_all_l_cn": "away_losses",
            # Recent 5 games
            "home_team_5_w_cn": "home_recent_wins",
            "home_team_5_l_cn": "home_recent_losses",
            "away_team_5_w_cn": "away_recent_wins",
            "away_team_5_l_cn": "away_recent_losses",
            "home_team_5_wdl": "home_recent_results",
            "away_team_5_wdl": "away_recent_results",
            # Win rates
            "home_team_all_wra_rt": "home_win_rate",
            "away_team_all_wra_rt": "away_win_rate",
            "home_team_h_wra_rt": "home_home_win_rate",
            "away_team_h_wra_rt": "away_home_win_rate",
            "home_team_a_wra_rt": "home_away_win_rate",
            "away_team_a_wra_rt": "away_away_win_rate",
            # Scoring
            "home_team_all_r_score": "home_avg_points",
            "away_team_all_r_score": "away_avg_points",
            "home_team_all_l_score": "home_avg_points_against",
            "away_team_all_l_score": "away_avg_points_against",
            # Shooting
            "home_team_fgp_rt": "home_fg_pct",
            "away_team_fgp_rt": "away_fg_pct",
            "home_team_p3_rt": "home_3p_pct",
            "away_team_p3_rt": "away_3p_pct",
            # Stats
            "home_team_assist_cn": "home_avg_assists",
            "away_team_assist_cn": "away_avg_assists",
            "home_team_turnover_cn": "home_avg_turnovers",
            "away_team_turnover_cn": "away_avg_turnovers",
            "home_team_steal_cn": "home_avg_steals",
            "away_team_steal_cn": "away_avg_steals",
            "home_team_reb_cn": "home_avg_rebounds",
            "away_team_reb_cn": "away_avg_rebounds",
            "home_team_dr_avg": "home_avg_def_rebounds",
            "away_team_dr_avg": "away_avg_def_rebounds",
            "home_team_blk_avg": "home_avg_blocks",
            "away_team_blk_avg": "away_avg_blocks",
            "home_team_pf_avg": "home_avg_fouls",
            "away_team_pf_avg": "away_avg_fouls",
            "home_league_id": "home_league_id",
        }

    def map_team_vs_list(self, response: Any) -> Dict[str, Any]:
        """Map team vs team API response to standardized format.

        Args:
            response: Raw API response

        Returns:
            Team comparison data with mapped field names
        """
        data = response.get("Data", {})
        items = data.get("list", [])

        if not items:
            return {}

        field_map = self.get_team_vs_list_field_map()
        return self._apply_field_mapping(items[0], field_map)

    def get_position_map(self) -> Dict[str, str]:
        """Return basketball position code -> display name mapping."""
        return self.POSITION_MAP

    def get_starter_positions(self) -> Set[str]:
        """Return basketball starter position codes."""
        return self.STARTER_POSITIONS

    def build_game_records(
        self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build basketball-specific game records for display.

        Args:
            home_stats: Home team statistics
            away_stats: Away team statistics

        Returns:
            List of game record dicts with basketball stats
        """
        # Field goals
        home_fgm = _safe_int(home_stats.get("home_team_fgm_cn"), 0)
        home_fga = _safe_int(home_stats.get("home_team_fga_cn"), 1)
        away_fgm = _safe_int(away_stats.get("away_team_fgm_cn"), 0)
        away_fga = _safe_int(away_stats.get("away_team_fga_cn"), 1)

        # 3-pointers
        home_3pm = _safe_int(home_stats.get("home_team_pgm3_cn"), 0)
        home_3pa = _safe_int(home_stats.get("home_team_pga3_cn"), 1)
        away_3pm = _safe_int(away_stats.get("away_team_pgm3_cn"), 0)
        away_3pa = _safe_int(away_stats.get("away_team_pga3_cn"), 1)

        # Free throws
        home_ftm = _safe_int(home_stats.get("home_team_ftm_cn"), 0)
        home_fta = _safe_int(home_stats.get("home_team_fta_cn"), 1)
        away_ftm = _safe_int(away_stats.get("away_team_ftm_cn"), 0)
        away_fta = _safe_int(away_stats.get("away_team_fta_cn"), 1)

        # Rebounds
        home_oreb = _safe_int(home_stats.get("home_team_oreb_cn"), 0)
        home_dreb = _safe_int(home_stats.get("home_team_dreb_cn"), 0)
        away_oreb = _safe_int(away_stats.get("away_team_oreb_cn"), 0)
        away_dreb = _safe_int(away_stats.get("away_team_dreb_cn"), 0)

        # Other stats
        home_ast = _safe_int(home_stats.get("home_team_assist_cn"), 0)
        away_ast = _safe_int(away_stats.get("away_team_assist_cn"), 0)

        home_tov = _safe_int(home_stats.get("home_team_turnover_cn"), 0)
        away_tov = _safe_int(away_stats.get("away_team_turnover_cn"), 0)

        home_stl = _safe_int(home_stats.get("home_team_steal_cn"), 0)
        away_stl = _safe_int(away_stats.get("away_team_steal_cn"), 0)

        home_blk = _safe_int(home_stats.get("home_team_block_cn"), 0)
        away_blk = _safe_int(away_stats.get("away_team_block_cn"), 0)

        home_pf = _safe_int(home_stats.get("home_team_pfoul_cn"), 0)
        away_pf = _safe_int(away_stats.get("away_team_pfoul_cn"), 0)

        return [
            {"label": "필드골", "home": f"{home_fgm}/{home_fga}", "away": f"{away_fgm}/{away_fga}"},
            {"label": "3점슛", "home": f"{home_3pm}/{home_3pa}", "away": f"{away_3pm}/{away_3pa}"},
            {"label": "자유투", "home": f"{home_ftm}/{home_fta}", "away": f"{away_ftm}/{away_fta}"},
            {"label": "리바운드", "home": f"{home_oreb + home_dreb}", "away": f"{away_oreb + away_dreb}"},
            {"label": "어시스트", "home": home_ast, "away": away_ast},
            {"label": "턴오버", "home": home_tov, "away": away_tov},
            {"label": "스틸", "home": home_stl, "away": away_stl},
            {"label": "블록", "home": home_blk, "away": away_blk},
            {"label": "파울", "home": home_pf, "away": away_pf},
        ]
