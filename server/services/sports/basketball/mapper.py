"""Basketball-specific response mapper."""
from typing import Dict, List, Any
from server.services.sports.base.mapper import BaseResponseMapper


class BasketballMapper(BaseResponseMapper):
    """Response mapper for Basketball API."""

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
            "home_team_id": "home_team_id",
            "away_team_id": "away_team_id",
            "home_group_sc": "home_conference",
            "away_group_sc": "away_conference",
            "home_team_rank": "home_rank",
            "away_team_rank": "away_rank",
            "home_team_all_w_cn": "home_wins",
            "away_team_all_w_cn": "away_wins",
            "home_team_all_l_cn": "home_losses",
            "away_team_all_l_cn": "away_losses",
            "home_team_5_w_cn": "home_recent_wins",
            "home_team_5_l_cn": "home_recent_losses",
            "away_team_5_w_cn": "away_recent_wins",
            "away_team_5_l_cn": "away_recent_losses",
            "home_team_all_wra_rt": "home_win_rate",
            "away_team_all_wra_rt": "away_win_rate",
            "home_team_h_wra_rt": "home_home_win_rate",
            "away_team_h_wra_rt": "away_home_win_rate",
            "home_team_a_wra_rt": "home_away_win_rate",
            "away_team_a_wra_rt": "away_away_win_rate",
            "home_team_all_r_score": "home_avg_points",
            "away_team_all_r_score": "away_avg_points",
            "home_team_all_l_score": "home_avg_points_against",
            "away_team_all_l_score": "away_avg_points_against",
            "home_team_fgp_rt": "home_fg_pct",
            "away_team_fgp_rt": "away_fg_pct",
            "home_team_p3_rt": "home_3p_pct",
            "away_team_p3_rt": "away_3p_pct",
            "home_team_assist_cn": "home_avg_assists",
            "away_team_assist_cn": "away_avg_assists",
            "home_team_turnover_cn": "home_avg_turnovers",
            "away_team_turnover_cn": "away_avg_turnovers",
            "home_team_steal_cn": "home_avg_steals",
            "away_team_steal_cn": "away_avg_steals",
            "home_team_reb_cn": "home_avg_rebounds",
            "away_team_reb_cn": "away_avg_rebounds",
            "home_team_blk_avg": "home_avg_blocks",
            "away_team_blk_avg": "away_avg_blocks",
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
