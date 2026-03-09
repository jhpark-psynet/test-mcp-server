"""축구 전용 핸들러 함수."""
import logging
from typing import Any, Dict, Optional

from server.handlers._common import safe_int, _calc_percentage

logger = logging.getLogger(__name__)


def _get_soccer_position(formation_place: str) -> str:
  """포메이션 위치를 포지션 문자열로 변환."""
  position_map = {
    "0": "-",       # 벤치/미출전
    "1": "GK",      # 골키퍼
    "2": "DF",      # 수비 (RB)
    "3": "DF",      # 수비 (LB)
    "4": "DF",      # 수비 (CB)
    "5": "DF",      # 수비 (CB)
    "6": "MF",      # 미드필더 (CDM)
    "7": "FW",      # 공격 (LW)
    "8": "MF",      # 미드필더 (CM)
    "9": "FW",      # 공격 (ST)
    "10": "MF",     # 미드필더 (CAM)
    "11": "FW",     # 공격 (RW)
  }
  return position_map.get(formation_place, "MF")


def _build_soccer_player_data(
  player: Dict[str, Any],
  lineup_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
  """축구 선수 개별 데이터 생성.

  프론트엔드 SoccerPlayerStats 인터페이스에 맞춤:
  - number, name, position, minutes
  - goals, assists, shots, shotsOnTarget
  - passes, passAccuracy, tackles, interceptions
  - fouls, yellowCards, redCards, saves

  Args:
    player: 선수 통계 데이터 (soccerPlayerStat API)
    lineup_map: lineup에서 가져온 선수 정보 {player_id: {name, number}}
  """
  # 포지션 변환 (formationPlace -> display position)
  formation_place = str(player.get("formation_place", player.get("formationPlace", "0")))
  position = _get_soccer_position(formation_place)

  # 출전 시간 (분 단위)
  mins_played = safe_int(player.get("mins_played", player.get("minsPlayed")), 0)

  # 패스 성공률 계산
  total_passes = safe_int(player.get("total_passes", player.get("totalPass")), 0)
  accurate_passes = safe_int(player.get("accurate_passes", player.get("accuratePass")), 0)
  pass_accuracy = ""
  if total_passes > 0:
    pass_accuracy = f"{round(accurate_passes / total_passes * 100)}%"

  # 선수 이름/등번호: lineup에서 가져오기 (soccerPlayerStat에는 없음)
  player_id = player.get("player_id") or player.get("PLAYER_ID", "")
  lineup_info = lineup_map.get(player_id, {}) if lineup_map else {}
  player_name = lineup_info.get("name") or player.get("player_name") or "Unknown"
  player_number = lineup_info.get("number") or safe_int(player.get("back_no"), 0)

  return {
    # 기본 정보 (lineup API에서 가져옴)
    "number": player_number,
    "name": player_name,
    "position": position,
    "minutes": mins_played,

    # 공격 스탯
    "goals": safe_int(player.get("goals", player.get("Goals")), 0),
    "assists": safe_int(player.get("assists", player.get("goalAssist")), 0),
    "shots": safe_int(player.get("total_shots", player.get("totalScoringAtt")), 0),
    "shotsOnTarget": safe_int(player.get("shots_on_target", player.get("ontargetScoringAtt")), 0),

    # 패스 스탯
    "passes": total_passes,
    "passAccuracy": pass_accuracy,

    # 수비 스탯
    "tackles": safe_int(player.get("tackles", player.get("totalTackle")), 0),
    "interceptions": safe_int(player.get("interceptions", player.get("interception")), 0),

    # 파울/카드
    "fouls": safe_int(player.get("fouls"), 0),
    "yellowCards": safe_int(player.get("yellow_cards", player.get("yellowCard")), 0),
    "redCards": safe_int(player.get("red_cards", player.get("redCard")), 0),

    # 골키퍼 스탯 (GK인 경우만 의미 있음)
    "saves": safe_int(player.get("saves"), 0),
  }


async def get_player_season_stats_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
  """선수 시즌 통계를 조회하는 핸들러.

  Args:
    arguments: 요청 파라미터
      - league_id: 리그 ID (필수)
      - season_id: 시즌 ID (필수)
      - team_id: 팀 ID (필수)
      - player_id: 선수 ID (필수)

  Returns:
    선수 시즌 통계 딕셔너리

  Raises:
    ValueError: 필수 파라미터 누락 또는 데이터 없음
  """
  league_id = arguments.get("league_id", "").strip()
  season_id = arguments.get("season_id", "").strip()
  team_id = arguments.get("team_id", "").strip()
  player_id = arguments.get("player_id", "").strip()

  # 필수 파라미터 검증
  missing_params = []
  if not league_id:
    missing_params.append("league_id")
  if not season_id:
    missing_params.append("season_id")
  if not team_id:
    missing_params.append("team_id")
  if not player_id:
    missing_params.append("player_id")

  if missing_params:
    raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

  # Soccer 클라이언트 생성 (현재 soccer만 지원)
  from server.services.sports.soccer import SoccerClient
  client = SoccerClient()

  # 시즌 통계 조회
  stats_list = await client.get_player_season_stats(
    league_id=league_id,
    season_id=season_id,
    team_id=team_id,
    player_id=player_id,
  )

  if not stats_list:
    raise ValueError(
      f"No season stats found for player {player_id} "
      f"(league={league_id}, season={season_id}, team={team_id})"
    )

  # 첫 번째 결과 반환 (일반적으로 1개만 있음)
  stats = stats_list[0]

  # 응답 구조화 (카테고리별 그룹화)
  return {
    "leagueId": league_id,
    "seasonId": season_id,
    "teamId": team_id,
    "playerId": player_id,
    "stats": {
      "passing": {
        "totalPass": safe_int(stats.get("total_pass"), 0),
        "accuratePass": safe_int(stats.get("accurate_pass"), 0),
        "passAccuracy": _calc_percentage(
          stats.get("accurate_pass"), stats.get("total_pass")
        ),
        "totalFinalThirdPasses": safe_int(stats.get("total_final_third_passes"), 0),
        "successfulFinalThirdPasses": safe_int(stats.get("successful_final_third_passes"), 0),
        "totalThroughBall": safe_int(stats.get("total_through_ball"), 0),
        "successfulPutThrough": safe_int(stats.get("successful_put_through"), 0),
      },
      "shooting": {
        "goals": safe_int(stats.get("goals"), 0),
        "totalScoringAtt": safe_int(stats.get("total_scoring_att"), 0),
        "ontargetScoringAtt": safe_int(stats.get("ontarget_scoring_att"), 0),
        "shotAccuracy": _calc_percentage(
          stats.get("ontarget_scoring_att"), stats.get("total_scoring_att")
        ),
        "goalsOpenplay": safe_int(stats.get("goals_openplay"), 0),
        "winningGoal": safe_int(stats.get("winning_goal"), 0),
        "bigChanceMissed": safe_int(stats.get("big_chance_missed"), 0),
      },
      "possession": {
        "touches": safe_int(stats.get("touches"), 0),
        "touchesInFinalThird": safe_int(stats.get("touches_in_final_third"), 0),
        "touchesInOppBox": safe_int(stats.get("touches_in_opp_box"), 0),
        "carries": safe_int(stats.get("carries"), 0),
        "progressiveCarries": safe_int(stats.get("progressive_carries"), 0),
        "dispossessed": safe_int(stats.get("dispossessed"), 0),
        "turnover": safe_int(stats.get("turnover"), 0),
      },
      "duel": {
        "duelWon": safe_int(stats.get("duel_won"), 0),
        "duelLost": safe_int(stats.get("duel_lost"), 0),
        "duelWinRate": _calc_percentage(
          stats.get("duel_won"),
          safe_int(stats.get("duel_won"), 0) + safe_int(stats.get("duel_lost"), 0)
        ),
        "totalTackle": safe_int(stats.get("total_tackle"), 0),
        "totalContest": safe_int(stats.get("total_contest"), 0),
        "wonContest": safe_int(stats.get("won_contest"), 0),
      },
      "defense": {
        "ballRecovery": safe_int(stats.get("ball_recovery"), 0),
        "possWonDef3rd": safe_int(stats.get("poss_won_def_3rd"), 0),
        "possWonMid3rd": safe_int(stats.get("poss_won_mid_3rd"), 0),
        "goalsConceded": safe_int(stats.get("goals_conceded"), 0),
      },
      "appearance": {
        "minsPlayed": safe_int(stats.get("mins_played"), 0),
        "totalSubOn": safe_int(stats.get("total_sub_on"), 0),
      },
    },
  }
