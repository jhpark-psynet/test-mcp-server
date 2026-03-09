"""야구 전용 핸들러 함수."""
import logging
from typing import Any, Dict, List

from server.handlers._common import safe_int, get_team_logo_url, build_recent_games

logger = logging.getLogger(__name__)


def _build_inning_scores(inning_scores_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  """야구 이닝별 점수 파싱."""
  result = []
  for idx, inning in enumerate(inning_scores_raw):
    inning_no = safe_int(inning.get("inning_no"))
    if inning_no == 0:
      inning_no = idx + 1  # fallback: 배열 순서로 이닝 번호 추론
    result.append({
      "inning": inning_no,
      "homeScore": str(inning.get("home_score", "-")).strip(),
      "awayScore": str(inning.get("away_score", "-")).strip(),
    })
  return result


def _build_baseball_batters(batters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  """야구 타자 스탯 빌드."""
  result = []
  for b in batters:
    result.append({
      "batOrder": safe_int(b.get("bat_order_no")),
      "name": b.get("player_name", "Unknown"),
      "position": b.get("pos_sc", "-"),
      "atBats": safe_int(b.get("ab_cn")),
      "hits": safe_int(b.get("hit_cn")),
      "homeRuns": safe_int(b.get("hr_cn")),
      "rbi": safe_int(b.get("rbi_cn")),
      "walks": safe_int(b.get("bb_cn")),
      "strikeouts": safe_int(b.get("kk_cn")),
      "avg": str(b.get("hra_rt", ".000")),
      "obp": str(b.get("obp_rt", ".000")),
      "ops": str(b.get("ops_rt", ".000")),
    })
  return result


def _build_baseball_pitchers(pitchers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  """야구 투수 스탯 빌드."""
  result = []
  for p in pitchers:
    result_str = ""
    if p.get("w_yn") == "Y":
      result_str = "승"
    elif p.get("l_yn") == "Y":
      result_str = "패"
    elif p.get("s_yn") == "Y":
      result_str = "세"
    elif p.get("h_yn") == "Y":
      result_str = "홀"
    elif p.get("bs_yn") == "Y":
      result_str = "BS"

    result.append({
      "turnNo": safe_int(p.get("turn_no")),
      "name": p.get("player_name", "Unknown"),
      "result": result_str,
      "innings": str(p.get("pitch_inning", "0")),
      "pitchCount": safe_int(p.get("pit_cn")),
      "hits": safe_int(p.get("hit_cn")),
      "strikeouts": safe_int(p.get("kk_cn")),
      "runs": safe_int(p.get("r_cn")),
      "earnedRuns": safe_int(p.get("er_cn")),
      "era": str(p.get("era_rt", "0.00")),
      "whip": str(p.get("whip_rt", "0.00")),
    })
  return result


def _build_baseball_recent_games(vs_info: Dict[str, Any], side: str) -> List[str]:
  """야구 최근 5경기 결과 빌드."""
  if not vs_info:
    return []
  wdl_str = vs_info.get(f"{side}_team_5_wdl", "")
  if wdl_str:
    return [r.strip() for r in wdl_str.split(",") if r.strip() in ("W", "L", "D")]
  wins = safe_int(vs_info.get(f"{side}_team_5_w_cn"))
  losses = safe_int(vs_info.get(f"{side}_team_5_l_cn"))
  return build_recent_games(wins, losses)


def _build_baseball_record_string(team_info: Dict[str, Any], side: str) -> str:
  """야구 팀 성적 문자열 빌드."""
  wins = safe_int(team_info.get(f"{side}_team_w_cn"))
  draws = safe_int(team_info.get(f"{side}_team_d_cn"))
  losses = safe_int(team_info.get(f"{side}_team_l_cn"))
  if wins == 0 and draws == 0 and losses == 0:
    return ""
  if draws > 0:
    return f"{wins}승 {draws}무 {losses}패"
  return f"{wins}승 {losses}패"


async def build_baseball_game_response(
  client: Any, game_id: str
) -> Dict[str, Any]:
  """야구 경기 상세 응답 빌드 (단일 API 호출).

  Args:
    client: BaseballClient instance
    game_id: Game ID

  Returns:
    Complete baseball game data dict for the widget
  """
  total_info = await client.get_game_total_info(game_id)

  game_info = total_info.get("gameInfo", {})

  home_team_name = game_info.get("home_team_name") or ""
  away_team_name = game_info.get("away_team_name") or ""
  if not home_team_name and not away_team_name:
    raise ValueError("경기 데이터를 불러올 수 없습니다")

  home_team_info = total_info.get("homeTeamInfo", {})
  away_team_info = total_info.get("awayTeamInfo", {})
  total_stat_info = total_info.get("totalStatInfo", {})
  inning_scores_raw = total_info.get("inningScore", [])
  vs_info = total_info.get("vsInfo", {})
  pitcher_stat = total_info.get("pitcherStat", {})
  batter_stat = total_info.get("batterStat", {})

  # Basic game info
  match_date = game_info.get("match_date", "")
  formatted_date = f"{match_date[4:6]}.{match_date[6:8]}" if len(match_date) >= 8 else ""

  status_map = client.get_status_map()
  state_raw = str(game_info.get("state") or game_info.get("game_status") or "F").upper()
  status = status_map.get(state_raw, "종료")

  home_team_id = game_info.get("home_team_id", "")
  away_team_id = game_info.get("away_team_id", "")

  # Inning scores (shared between home and away teams)
  inning_scores = _build_inning_scores(inning_scores_raw)

  # Batter/pitcher lists
  home_batters = _build_baseball_batters(batter_stat.get("home", []))
  away_batters = _build_baseball_batters(batter_stat.get("away", []))
  home_pitchers = _build_baseball_pitchers(pitcher_stat.get("home", []))
  away_pitchers = _build_baseball_pitchers(pitcher_stat.get("away", []))

  # Game records from totalStatInfo
  game_records: List[Dict[str, Any]] = []
  if total_stat_info:
    game_records = client.mapper.build_game_records(total_stat_info, total_stat_info)

  # Recent games and records
  home_recent = _build_baseball_recent_games(vs_info, "home")
  away_recent = _build_baseball_recent_games(vs_info, "away")
  home_record = _build_baseball_record_string(home_team_info, "home")
  away_record = _build_baseball_record_string(away_team_info, "away")

  # Scores: prefer totalStatInfo, fallback to inning sum
  home_score = safe_int(total_stat_info.get("home_team_score_cn"))
  away_score = safe_int(total_stat_info.get("away_team_score_cn"))

  # Fallback: sum inning scores when totalStatInfo has no score data
  if home_score == 0 and away_score == 0 and inning_scores:
    calc_home = sum(safe_int(s["homeScore"]) for s in inning_scores)
    calc_away = sum(safe_int(s["awayScore"]) for s in inning_scores)
    if calc_home > 0 or calc_away > 0:
      home_score = calc_home
      away_score = calc_away

  # League normalization
  league_name = game_info.get("league_name") or "KBO리그"
  league = league_name

  result: Dict[str, Any] = {
    "sportType": "baseball",
    "league": league,
    "date": formatted_date,
    "status": status,
    "homeTeam": {
      "name": home_team_name or "Home",
      "shortName": home_team_name or "Home",
      "logo": get_team_logo_url(home_team_id),
      "score": home_score,
      "record": home_record,
      "inningScores": inning_scores,
      "batters": home_batters,
      "pitchers": home_pitchers,
      "recentGames": home_recent,
      "teamHits": safe_int(total_stat_info.get("home_team_hit_cn")),
      "teamErrors": safe_int(total_stat_info.get("home_team_err_cn")),
    },
    "awayTeam": {
      "name": away_team_name or "Away",
      "shortName": away_team_name or "Away",
      "logo": get_team_logo_url(away_team_id),
      "score": away_score,
      "record": away_record,
      "inningScores": inning_scores,
      "batters": away_batters,
      "pitchers": away_pitchers,
      "recentGames": away_recent,
      "teamHits": safe_int(total_stat_info.get("away_team_hit_cn")),
      "teamErrors": safe_int(total_stat_info.get("away_team_err_cn")),
    },
    "gameRecords": game_records,
  }

  # Optional fields
  if game_info.get("match_time"):
    result["time"] = game_info["match_time"]
  if game_info.get("arena_name"):
    result["venue"] = game_info["arena_name"]
  if game_info.get("home_starter_name"):
    result["homeStarterName"] = game_info["home_starter_name"]
  if game_info.get("away_starter_name"):
    result["awayStarterName"] = game_info["away_starter_name"]

  # Head-to-head
  if vs_info:
    home_vs_wins = safe_int(vs_info.get("home_team_vs_w_cn"))
    home_vs_losses = safe_int(vs_info.get("home_team_vs_l_cn"))
    home_vs_draws = safe_int(vs_info.get("home_team_vs_d_cn"))
    away_vs_wins = safe_int(vs_info.get("away_team_vs_w_cn"))
    total_h2h = home_vs_wins + home_vs_losses + home_vs_draws
    if total_h2h > 0:
      result["headToHead"] = {
        "totalGames": total_h2h,
        "homeWins": home_vs_wins,
        "awayWins": away_vs_wins,
        "draws": home_vs_draws,
      }

  logger.info(
    f"[build_baseball_game_response] Returning data for "
    f"{game_info.get('home_team_name')} vs {game_info.get('away_team_name')}"
  )
  return result
