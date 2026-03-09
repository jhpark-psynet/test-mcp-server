"""농구 전용 핸들러 함수."""
import logging
from typing import Any, Dict, List

from server.handlers._common import safe_int, safe_float, get_team_logo_url, build_recent_games

logger = logging.getLogger(__name__)


def _build_basketball_player_data(player: Dict[str, Any]) -> Dict[str, Any]:
  """농구 선수 개별 데이터 생성.

  totalInfo lineup 필드명(tot_pts, position)과
  기존 playerStat 필드명(tot_score, pos_sc) 모두 지원.
  """
  # 출전 시간 파싱 (MM:SS 형식)
  player_time = player.get("player_time", "0:00")
  minutes = 0
  try:
    time_parts = str(player_time).split(":")
    if len(time_parts) >= 2:
      minutes = int(time_parts[0]) * 60 + int(time_parts[1])
      minutes = round(minutes / 60)
    else:
      minutes = safe_int(player_time, 0)
  except (ValueError, AttributeError):
    minutes = 0

  fgm = safe_int(player.get("fgm_cn"))
  fga = safe_int(player.get("fga") or player.get("fga_cn"))
  tpm = safe_int(player.get("pgm3_cn"))
  tpa = safe_int(player.get("pga3") or player.get("pga3_cn"))
  steals = safe_int(player.get("steal_cn"))
  blocks = safe_int(player.get("block_cn"))

  data: Dict[str, Any] = {
    "number": safe_int(player.get("back_no"), 0),
    "name": player.get("player_name", "Unknown"),
    "position": player.get("position") or player.get("pos_sc", "-"),
    "minutes": minutes,
    "points": safe_int(player.get("tot_pts") or player.get("tot_score"), 0),
    "rebounds": safe_int(player.get("treb_cn"), 0),
    "assists": safe_int(player.get("assist_cn"), 0),
  }
  if fgm is not None or fga is not None:
    data["fgm"] = fgm or 0
    data["fga"] = fga or 0
  if tpm is not None or tpa is not None:
    data["tpm"] = tpm or 0
    data["tpa"] = tpa or 0
  if steals:
    data["steals"] = steals
  if blocks:
    data["blocks"] = blocks
  return data


def _build_basketball_recent_games(vs_info: Dict[str, Any], side: str) -> List[str]:
  """vsInfo에서 최근 5경기 결과 배열 생성."""
  if not vs_info:
    return []
  wins = safe_int(vs_info.get(f"{side}_team_5_w_cn"))
  losses = safe_int(vs_info.get(f"{side}_team_5_l_cn"))
  return build_recent_games(wins, losses)


def _build_quarter_scores(score_info: Dict[str, Any], side: str):
  """scoreInfo에서 쿼터별 점수 dict 생성. 데이터 없으면 None 반환."""
  q1 = safe_int(score_info.get(f"{side}_1q_point"))
  q2 = safe_int(score_info.get(f"{side}_2q_point"))
  q3 = safe_int(score_info.get(f"{side}_3q_point"))
  q4 = safe_int(score_info.get(f"{side}_4q_point"))
  if q1 == 0 and q2 == 0 and q3 == 0 and q4 == 0:
    return None
  qs: Dict[str, Any] = {"q1": q1, "q2": q2, "q3": q3, "q4": q4}
  ot_scores = [safe_int(score_info.get(f"{side}_{i}ot_point")) for i in range(1, 4)]
  ot_scores = [s for s in ot_scores if s and s > 0]
  if ot_scores:
    qs["ot"] = ot_scores
  return qs


def _build_basketball_record(team_info: Dict[str, Any], side: str) -> str:
  """팀 시즌 성적 문자열 생성."""
  wins = safe_int(team_info.get(f"{side}_w_cn"))
  losses = safe_int(team_info.get(f"{side}_l_cn"))
  if wins == 0 and losses == 0:
    return ""
  return f"{wins}승 {losses}패"


def _build_team_comparison(
  home_info: Dict[str, Any], away_info: Dict[str, Any]
) -> Dict[str, Any]:
  """homeTeamInfo / awayTeamInfo 기반 팀 비교 데이터 생성."""
  if not home_info and not away_info:
    return {}
  return {
    "home": {
      "winRate": str(home_info.get("home_wpct_rt", "0")),
      "avgPoints": safe_float(home_info.get("home_pts_cn")),
      "avgPointsAgainst": 0.0,
      "fgPct": str(home_info.get("home_fgp_rt", "0")),
      "threePct": str(home_info.get("home_p3_rt", "0")),
      "avgRebounds": safe_float(home_info.get("home_reb_cn")),
      "avgAssists": safe_float(home_info.get("home_assist_cn")),
      "avgSteals": 0.0,
      "avgBlocks": 0.0,
      "avgTurnovers": safe_float(home_info.get("home_turnover_cn")),
    },
    "away": {
      "winRate": str(away_info.get("away_wpct_rt", "0")),
      "avgPoints": safe_float(away_info.get("away_pts_cn")),
      "avgPointsAgainst": 0.0,
      "fgPct": str(away_info.get("away_fgp_rt", "0")),
      "threePct": str(away_info.get("away_p3_rt", "0")),
      "avgRebounds": safe_float(away_info.get("away_reb_cn")),
      "avgAssists": safe_float(away_info.get("away_assist_cn")),
      "avgSteals": 0.0,
      "avgBlocks": 0.0,
      "avgTurnovers": safe_float(away_info.get("away_turnover_cn")),
    },
  }


def _aggregate_player_stats_to_team(
  players: List[Dict[str, Any]], side: str
) -> Dict[str, Any]:
  """선수 통계 목록을 팀 합계로 집계 (build_game_records 입력 형식)."""
  team_players = players
  return {
    f"{side}_team_fgm_cn": sum(safe_int(p.get("fgm_cn")) for p in team_players),
    f"{side}_team_fga_cn": sum(safe_int(p.get("fga_cn")) for p in team_players),
    f"{side}_team_pgm3_cn": sum(safe_int(p.get("pgm3_cn")) for p in team_players),
    f"{side}_team_pga3_cn": sum(safe_int(p.get("pga3_cn")) for p in team_players),
    f"{side}_team_ftm_cn": sum(safe_int(p.get("ftm_cn")) for p in team_players),
    f"{side}_team_fta_cn": sum(safe_int(p.get("fta_cn")) for p in team_players),
    f"{side}_team_oreb_cn": sum(safe_int(p.get("oreb_cn")) for p in team_players),
    f"{side}_team_dreb_cn": sum(safe_int(p.get("dreb_cn")) for p in team_players),
    f"{side}_team_assist_cn": sum(safe_int(p.get("assist_cn")) for p in team_players),
    f"{side}_team_turnover_cn": sum(safe_int(p.get("turnover_cn")) for p in team_players),
    f"{side}_team_steal_cn": sum(safe_int(p.get("steal_cn")) for p in team_players),
    f"{side}_team_block_cn": sum(safe_int(p.get("block_cn")) for p in team_players),
    f"{side}_team_pfoul_cn": sum(safe_int(p.get("pfoul_cn")) for p in team_players),
  }


async def build_basketball_game_response(
  client: Any, game_id: str
) -> Dict[str, Any]:
  """농구 경기 상세 응답 빌드 (단일 basketballGameTotalInfo API 호출).

  Args:
    client: BasketballClient instance
    game_id: Game ID

  Returns:
    Complete basketball game data dict for the widget
  """
  data = await client.get_total_info(game_id)

  game_info = data.get("gameInfo", {})
  home_team_name = game_info.get("home_team_name") or ""
  away_team_name = game_info.get("away_team_name") or ""
  if not home_team_name and not away_team_name:
    raise ValueError("경기 데이터를 불러올 수 없습니다")

  home_team_id = game_info.get("home_team_id", "")
  away_team_id = game_info.get("away_team_id", "")

  # 경기 상태
  game_status_raw = str(game_info.get("game_status") or "F").upper()
  status_map = {"B": "예정", "I": "진행중", "F": "종료"}
  status = status_map.get(game_status_raw, "종료")

  # 날짜 포맷
  match_date = game_info.get("match_date", "")
  formatted_date = f"{match_date[4:6]}.{match_date[6:8]}" if len(match_date) >= 8 else ""

  # 리그 이름
  league_id = game_info.get("league_id", "")
  _league_id_to_name = {v: k for k, v in client.get_league_id_map().items()}
  league_name = game_info.get("league_name") or _league_id_to_name.get(league_id) or "NBA"

  # 데이터 섹션 추출 (방어적 타입 체크)
  def _as_dict(val: Any) -> Dict[str, Any]:
    return val if isinstance(val, dict) else {}

  def _as_list(val: Any) -> List[Any]:
    return val if isinstance(val, list) else []

  home_info = _as_dict(data.get("homeTeamInfo"))
  away_info = _as_dict(data.get("awayTeamInfo"))
  vs_info = _as_dict(data.get("vsInfo"))
  score_info = _as_dict(data.get("scoreInfo"))
  # teamStat = {"home": [팀합계1행], "away": [팀합계1행]}
  team_stat_raw = data.get("teamStat")
  team_stat_dict = team_stat_raw if isinstance(team_stat_raw, dict) else {}
  home_stat_list = _as_list(team_stat_dict.get("home"))
  away_stat_list = _as_list(team_stat_dict.get("away"))

  # lineup = {"home": [선수별통계...], "away": [선수별통계...]}
  lineup_raw = data.get("lineup")
  lineup_dict = lineup_raw if isinstance(lineup_raw, dict) else {}
  home_lineup_list = _as_list(lineup_dict.get("home"))
  away_lineup_list = _as_list(lineup_dict.get("away"))

  # 스코어 (scoreInfo.home_total_score / away_total_score)
  home_score = safe_int(score_info.get("home_total_score"))
  away_score = safe_int(score_info.get("away_total_score"))

  # 최근 5경기
  home_recent = _build_basketball_recent_games(vs_info, "home")
  away_recent = _build_basketball_recent_games(vs_info, "away")

  # 시즌 성적
  home_record = _build_basketball_record(home_info, "home")
  away_record = _build_basketball_record(away_info, "away")

  # 선수 통계 (lineup 기반 - player_id 기준 중복 제거)
  def _dedup_by_player_id(players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set = set()
    result = []
    for p in players:
      pid = p.get("player_id") or p.get("back_no")
      if pid not in seen:
        seen.add(pid)
        result.append(p)
    return result

  home_players = [_build_basketball_player_data(p) for p in _dedup_by_player_id(home_lineup_list)]
  away_players = [_build_basketball_player_data(p) for p in _dedup_by_player_id(away_lineup_list)]
  home_players.sort(key=lambda x: x.get("minutes", 0), reverse=True)
  away_players.sort(key=lambda x: x.get("minutes", 0), reverse=True)

  # 게임 레코드 (teamStat 팀 합계 1행 기반)
  game_records: List[Dict[str, Any]] = []
  home_team_row = home_stat_list[0] if home_stat_list else {}
  away_team_row = away_stat_list[0] if away_stat_list else {}
  if home_team_row or away_team_row:
    # build_game_records 는 home_team_fgm_cn 형식 키를 기대하므로 prefix 추가
    home_agg = {f"home_team_{k}": v for k, v in home_team_row.items()}
    away_agg = {f"away_team_{k}": v for k, v in away_team_row.items()}
    game_records = client.mapper.build_game_records(home_agg, away_agg)

  # 쿼터별 점수 (경기중/종료만)
  home_quarter_scores = None
  away_quarter_scores = None
  if status in ("진행중", "종료") and score_info:
    home_quarter_scores = _build_quarter_scores(score_info, "home")
    away_quarter_scores = _build_quarter_scores(score_info, "away")

  home_team_dict: Dict[str, Any] = {
    "name": home_team_name,
    "shortName": home_team_name,
    "logo": get_team_logo_url(home_team_id),
    "record": home_record,
    "score": home_score,
    "players": home_players,
    "recentGames": home_recent,
  }
  if home_quarter_scores:
    home_team_dict["quarterScores"] = home_quarter_scores

  away_team_dict: Dict[str, Any] = {
    "name": away_team_name,
    "shortName": away_team_name,
    "logo": get_team_logo_url(away_team_id),
    "record": away_record,
    "score": away_score,
    "players": away_players,
    "recentGames": away_recent,
  }
  if away_quarter_scores:
    away_team_dict["quarterScores"] = away_quarter_scores

  result: Dict[str, Any] = {
    "sportType": "basketball",
    "league": league_name,
    "date": formatted_date,
    "status": status,
    "homeTeam": home_team_dict,
    "awayTeam": away_team_dict,
    "gameRecords": game_records,
  }

  # 선택적 필드
  if game_info.get("match_time"):
    result["time"] = game_info["match_time"]
  if game_info.get("arena_name"):
    result["venue"] = game_info["arena_name"]

  # 팀 비교
  team_comparison = _build_team_comparison(home_info, away_info)
  if team_comparison:
    result["teamComparison"] = team_comparison

  # 상대전적
  if vs_info:
    home_h2h_wins = safe_int(vs_info.get("home_team_vs_w_cn"))
    home_h2h_losses = safe_int(vs_info.get("home_team_vs_l_cn"))
    away_h2h_wins = safe_int(vs_info.get("away_team_vs_w_cn"))
    total_h2h = home_h2h_wins + home_h2h_losses
    if total_h2h > 0:
      result["headToHead"] = {
        "totalGames": total_h2h,
        "homeWins": home_h2h_wins,
        "awayWins": away_h2h_wins,
        "draws": 0,
      }

  logger.info(
    f"[build_basketball_game_response] Returning data for "
    f"{home_team_name} vs {away_team_name} (status={status})"
  )
  return result
