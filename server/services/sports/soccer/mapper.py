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
        """Return field mapping for soccer team stats.

        Maps API field names to internal standardized field names.
        Based on soccerTeamStat API response structure.
        """
        return {
            # 식별자
            "GAME_ID": "game_id",
            "TEAM_ID": "team_id",
            "HOME_AWAY": "home_away",

            # 슈팅 관련
            "totalScoringAtt": "total_scoring_att",
            "ontargetScoringAtt": "ontarget_scoring_att",
            "shotOffTarget": "shot_off_target",
            "attemptsIbox": "attempts_ibox",
            "attemptsObox": "attempts_obox",
            "blockedScoringAtt": "blocked_scoring_att",
            "bigChanceCreated": "big_chance_created",
            "bigChanceMissed": "big_chance_missed",
            "bigChanceScored": "big_chance_scored",

            # 득점/실점
            "goals": "goals",
            "goalsIbox": "goals_ibox",
            "goalsObox": "goals_obox",
            "goalsOpenplay": "goals_openplay",
            "goalsConceded": "goals_conceded",
            "goalsConcededIbox": "goals_conceded_ibox",
            "goalsConcededObox": "goals_conceded_obox",
            "firstHalfGoals": "first_half_goals",

            # 패스 관련
            "totalPass": "total_pass",
            "accuratePass": "accurate_pass",
            "totalFinalThirdPasses": "total_final_third_passes",
            "successfulFinalThirdPasses": "successful_final_third_passes",
            "totalFwdZonePass": "total_fwd_zone_pass",
            "accurateFwdZonePass": "accurate_fwd_zone_pass",
            "totalBackZonePass": "total_back_zone_pass",
            "accurateBackZonePass": "accurate_back_zone_pass",
            "totalLongBalls": "total_long_balls",
            "accurateLongBalls": "accurate_long_balls",
            "totalChippedPass": "total_chipped_pass",
            "accurateChippedPass": "accurate_chipped_pass",
            "totalThroughBall": "total_through_ball",
            "accurateThroughBall": "accurate_through_ball",

            # 크로스
            "totalCross": "total_cross",
            "accurateCross": "accurate_cross",
            "totalCrossNocorner": "total_cross_nocorner",
            "accurateCrossNocorner": "accurate_cross_nocorner",
            "crosses18yard": "crosses_18yard",
            "crosses18yardplus": "crosses_18yardplus",
            "blockedCross": "blocked_cross",
            "effectiveBlockedCross": "effective_blocked_cross",

            # 점유 관련
            "possessionPercentage": "possession_percentage",
            "touches": "touches",
            "touchesInOppBox": "touches_in_opp_box",
            "finalThirdEntries": "final_third_entries",
            "penAreaEntries": "pen_area_entries",
            "ballRecovery": "ball_recovery",
            "possLostAll": "poss_lost_all",
            "possLostCtrl": "poss_lost_ctrl",
            "possWonDef3rd": "poss_won_def_3rd",
            "possWonMid3rd": "poss_won_mid_3rd",
            "possWonAtt3rd": "poss_won_att_3rd",

            # 수비 관련
            "totalTackle": "total_tackle",
            "wonTackle": "won_tackle",
            "interception": "interception",
            "interceptionWon": "interception_won",
            "totalClearance": "total_clearance",
            "effectiveClearance": "effective_clearance",
            "headClearance": "head_clearance",
            "effectiveHeadClearance": "effective_head_clearance",
            "outfielderBlock": "outfielder_block",
            "sixYardBlock": "six_yard_block",
            "defensiveActions": "defensive_actions",

            # 듀얼/경합
            "duelWon": "duel_won",
            "duelLost": "duel_lost",
            "aerialWon": "aerial_won",
            "aerialLost": "aerial_lost",
            "totalContest": "total_contest",
            "wonContest": "won_contest",
            "challengeLost": "challenge_lost",
            "dispossessed": "dispossessed",

            # 파울/카드
            "fkFoulLost": "fk_foul_lost",
            "fkFoulWon": "fk_foul_won",
            "totalYellowCard": "total_yellow_card",
            "attemptedTackleFoul": "attempted_tackle_foul",
            "fouledFinalThird": "fouled_final_third",

            # 코너/세트피스
            "wonCorners": "won_corners",
            "lostCorners": "lost_corners",
            "cornerTaken": "corner_taken",
            "totalCornersIntobox": "total_corners_intobox",
            "accurateCornersIntobox": "accurate_corners_intobox",

            # 오프사이드
            "totalOffside": "total_offside",

            # 골키퍼 관련
            "saves": "saves",
            "savedIbox": "saved_ibox",
            "divingSave": "diving_save",
            "punches": "punches",
            "goodHighClaim": "good_high_claim",
            "totalHighClaim": "total_high_claim",
            "keeperThrows": "keeper_throws",
            "accurateKeeperThrows": "accurate_keeper_throws",
            "goalKicks": "goal_kicks",
            "accurateGoalKicks": "accurate_goal_kicks",

            # 기타
            "formationUsed": "formation_used",
            "totalThrows": "total_throws",
            "accurateThrows": "accurate_throws",
            "totalLaunches": "total_launches",
            "accurateLaunches": "accurate_launches",
            "subsMade": "subs_made",
            "subsGoals": "subs_goals",
            "totalFastbreak": "total_fastbreak",
            "shotFastbreak": "shot_fastbreak",
            "attFastbreak": "att_fastbreak",
            "ppda": "ppda",
            "errorLeadToShot": "error_lead_to_shot",
            "unsuccessfulTouch": "unsuccessful_touch",
        }

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer player stats.

        Maps API field names to internal standardized field names.
        Based on soccerPlayerStat API response structure.
        """
        return {
            # 기본 식별자
            "GAME_ID": "game_id",
            "TEAM_ID": "team_id",
            "PLAYER_ID": "player_id",
            "HOME_AWAY": "home_away",

            # 선수 기본 정보
            "formationPlace": "formation_place",
            "gameStarted": "game_started",
            "minsPlayed": "mins_played",

            # 공격 스탯
            "Goals": "goals",
            "goals": "goals",
            "goalsOpenplay": "goals_openplay",
            "winningGoal": "winning_goal",
            "totalScoringAtt": "total_shots",
            "ontargetScoringAtt": "shots_on_target",
            "shotOffTarget": "shots_off_target",
            "attemptsIbox": "shots_in_box",
            "attemptsObox": "shots_out_box",
            "blockedScoringAtt": "shots_blocked",

            # 어시스트/키패스
            "goalAssist": "assists",
            "goalAssistOpenplay": "assists_openplay",
            "totalAttAssist": "key_passes",
            "bigChanceCreated": "big_chances_created",

            # 패스 스탯
            "totalPass": "total_passes",
            "accuratePass": "accurate_passes",
            "totalFinalThirdPasses": "final_third_passes",
            "successfulFinalThirdPasses": "final_third_passes_accurate",
            "totalLongBalls": "long_balls",
            "accurateLongBalls": "long_balls_accurate",
            "totalCross": "crosses",
            "accurateCross": "crosses_accurate",

            # 수비 스탯
            "totalTackle": "tackles",
            "wonTackle": "tackles_won",
            "interception": "interceptions",
            "interceptionWon": "interceptions_won",
            "totalClearance": "clearances",
            "effectiveClearance": "clearances_effective",
            "outfielderBlock": "blocks",
            "aerialWon": "aerial_won",
            "aerialLost": "aerial_lost",

            # 소유 스탯
            "ballRecovery": "ball_recoveries",
            "possLostAll": "possession_lost",
            "dispossessed": "dispossessed",
            "Touches": "touches",
            "touches": "touches",
            "Carries": "carries",
            "carries": "carries",
            "progressiveCarries": "progressive_carries",

            # 파울/카드
            "fouls": "fouls",
            "wasFouled": "was_fouled",
            "yellowCard": "yellow_cards",
            "redCard": "red_cards",

            # 골키퍼 스탯
            "saves": "saves",
            "savedIbox": "saves_in_box",
            "divingSave": "diving_saves",
            "goalsConceded": "goals_conceded",
            "goalsConcededIbox": "goals_conceded_in_box",
            "Punches": "punches",
            "keeperPickUp": "keeper_pickups",

            # 기타
            "penAreaEntries": "pen_area_entries",
            "touchesInOppBox": "touches_in_opp_box",
            "touchesInFinalThird": "touches_in_final_third",
            "totalOffside": "offsides",
        }

    def build_game_records(
        self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build soccer-specific game records for display.

        Args:
            home_stats: Home team statistics (mapped via get_team_stats_field_map)
            away_stats: Away team statistics (mapped via get_team_stats_field_map)

        Returns:
            List of game record dicts with soccer stats
        """
        # Calculate pass accuracy
        home_pass_accuracy = self._calc_pass_accuracy(home_stats)
        away_pass_accuracy = self._calc_pass_accuracy(away_stats)

        return [
            {
                "label": "점유율",
                "home": f"{_safe_int(home_stats.get('possession_percentage'), 50)}%",
                "away": f"{_safe_int(away_stats.get('possession_percentage'), 50)}%",
            },
            {
                "label": "슈팅",
                "home": _safe_int(home_stats.get("total_scoring_att"), 0),
                "away": _safe_int(away_stats.get("total_scoring_att"), 0),
            },
            {
                "label": "유효슈팅",
                "home": _safe_int(home_stats.get("ontarget_scoring_att"), 0),
                "away": _safe_int(away_stats.get("ontarget_scoring_att"), 0),
            },
            {
                "label": "패스",
                "home": _safe_int(home_stats.get("total_pass"), 0),
                "away": _safe_int(away_stats.get("total_pass"), 0),
            },
            {
                "label": "패스 성공률",
                "home": home_pass_accuracy,
                "away": away_pass_accuracy,
            },
            {
                "label": "파울",
                "home": _safe_int(home_stats.get("fk_foul_lost"), 0),
                "away": _safe_int(away_stats.get("fk_foul_lost"), 0),
            },
            {
                "label": "코너킥",
                "home": _safe_int(home_stats.get("won_corners"), 0),
                "away": _safe_int(away_stats.get("won_corners"), 0),
            },
            {
                "label": "오프사이드",
                "home": _safe_int(home_stats.get("total_offside"), 0),
                "away": _safe_int(away_stats.get("total_offside"), 0),
            },
            {
                "label": "옐로카드",
                "home": _safe_int(home_stats.get("total_yellow_card"), 0),
                "away": _safe_int(away_stats.get("total_yellow_card"), 0),
            },
        ]

    def _calc_pass_accuracy(self, stats: Dict[str, Any]) -> str:
        """Calculate pass accuracy percentage.

        Args:
            stats: Team statistics

        Returns:
            Pass accuracy as percentage string (e.g., "85%")
        """
        total = _safe_int(stats.get("total_pass"), 0)
        accurate = _safe_int(stats.get("accurate_pass"), 0)
        if total == 0:
            return "-"
        return f"{round(accurate / total * 100)}%"

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

    def get_player_season_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer player season stats.

        Maps API field names (camelCase) to internal standardized field names (snake_case).
        Based on soccerPlayerSeasonStat API response structure.
        """
        return {
            # 패스 관련
            "accurateBackZonePass": "accurate_back_zone_pass",
            "accurateFlickOn": "accurate_flick_on",
            "accurateFwdZonePass": "accurate_fwd_zone_pass",
            "accurateLayoffs": "accurate_layoffs",
            "accuratePass": "accurate_pass",
            "backwardPass": "backward_pass",
            "blockedPass": "blocked_pass",
            "fwdPass": "fwd_pass",
            "headPass": "head_pass",
            "leftsidePass": "leftside_pass",
            "rightsidePass": "rightside_pass",
            "longPassOwnToOpp": "long_pass_own_to_opp",
            "longPassOwnToOppSuccess": "long_pass_own_to_opp_success",
            "openPlayPass": "open_play_pass",
            "passesLeft": "passes_left",
            "passesRight": "passes_right",
            "successfulFinalThirdPasses": "successful_final_third_passes",
            "successfulOpenPlayPass": "successful_open_play_pass",
            "successfulPutThrough": "successful_put_through",
            "totalBackZonePass": "total_back_zone_pass",
            "totalChippedPass": "total_chipped_pass",
            "totalFinalThirdPasses": "total_final_third_passes",
            "totalFlickOn": "total_flick_on",
            "totalFwdZonePass": "total_fwd_zone_pass",
            "totalLayoffs": "total_layoffs",
            "totalPass": "total_pass",
            "totalThroughBall": "total_through_ball",
            "putThrough": "put_through",

            # 슈팅/득점 관련
            "attBxCentre": "att_bx_centre",
            "attemptsIbox": "attempts_ibox",
            "attGoalHighRight": "att_goal_high_right",
            "attHdMiss": "att_hd_miss",
            "attHdTotal": "att_hd_total",
            "attIboxGoal": "att_ibox_goal",
            "attIboxMiss": "att_ibox_miss",
            "attLfGoal": "att_lf_goal",
            "attLfTotal": "att_lf_total",
            "attMissLeft": "att_miss_left",
            "attOpenplay": "att_openplay",
            "bigChanceMissed": "big_chance_missed",
            "Goals": "goals",
            "goalsOpenplay": "goals_openplay",
            "ontargetScoringAtt": "ontarget_scoring_att",
            "shotOffTarget": "shot_off_target",
            "totalScoringAtt": "total_scoring_att",
            "winningGoal": "winning_goal",

            # 수비/실점 관련
            "attemptsConcededIbox": "attempts_conceded_ibox",
            "attemptsConcededObox": "attempts_conceded_obox",
            "goalsConceded": "goals_conceded",
            "goalsConcededIbox": "goals_conceded_ibox",

            # 볼 소유/드리블 관련
            "ballRecovery": "ball_recovery",
            "carries": "carries",
            "dispossessed": "dispossessed",
            "finalThirdEntries": "final_third_entries",
            "penAreaEntries": "pen_area_entries",
            "possLostAll": "poss_lost_all",
            "possLostCtrl": "poss_lost_ctrl",
            "possWonDef3rd": "poss_won_def_3rd",
            "possWonMid3rd": "poss_won_mid_3rd",
            "progressiveCarries": "progressive_carries",
            "Touches": "touches",
            "touchesInFinalThird": "touches_in_final_third",
            "touchesInOppBox": "touches_in_opp_box",
            "turnover": "turnover",
            "unsuccessfulTouch": "unsuccessful_touch",

            # 대인 플레이
            "challengeLost": "challenge_lost",
            "duelLost": "duel_lost",
            "duelWon": "duel_won",
            "timesTackled": "times_tackled",
            "totalContest": "total_contest",
            "totalTackle": "total_tackle",
            "wonContest": "won_contest",

            # 출전 관련
            "formationPlace": "formation_place",
            "minsPlayed": "mins_played",
            "totalSubOn": "total_sub_on",
        }

    def map_player_season_stats(self, response: Any) -> List[Dict[str, Any]]:
        """Map player season stats API response to standardized format.

        Args:
            response: Raw API response

        Returns:
            List of player season stats with standardized field names
        """
        data = response.get("Data", {})
        items = data.get("list", [])
        field_map = self.get_player_season_stats_field_map()
        return [self._apply_field_mapping(item, field_map) for item in items]

    def get_team_rank_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer team rank (league standings).

        Maps API field names to internal standardized field names.
        Based on soccerTeamRank API response structure.
        """
        return {
            "RANK": "rank",
            "TEAM_ID": "team_id",
            "GROUP_SC": "group",
            "GAME_CN": "games_played",
            "ALL_WP": "points",
            "ALL_W_CN": "wins",
            "ALL_D_CN": "draws",
            "ALL_L_CN": "losses",
            "ALL_R_SCORE": "goals_for",
            "ALL_L_SCORE": "goals_against",
            "GROUP_TYPE": "group_type",
            "GROUP_NAME": "group_name",
        }

    def map_team_rank_list(self, response: Any) -> List[Dict[str, Any]]:
        """Map team rank API response to standardized format.

        Args:
            response: Raw API response

        Returns:
            List of team rankings with standardized field names and calculated fields
        """
        data = response.get("Data", {})
        items = data.get("list", [])
        field_map = self.get_team_rank_field_map()

        result = []
        for item in items:
            mapped = self._apply_field_mapping(item, field_map)

            # Calculate goal difference
            goals_for = _safe_int(mapped.get("goals_for"), 0)
            goals_against = _safe_int(mapped.get("goals_against"), 0)
            mapped["goal_diff"] = goals_for - goals_against

            # Calculate win rate (승점 / 최대 가능 승점)
            games = _safe_int(mapped.get("games_played"), 0)
            points = _safe_int(mapped.get("points"), 0)
            if games > 0:
                max_points = games * 3
                mapped["win_rate"] = f"{round(points / max_points * 100, 1)}%"
            else:
                mapped["win_rate"] = "0.0%"

            result.append(mapped)

        return result
