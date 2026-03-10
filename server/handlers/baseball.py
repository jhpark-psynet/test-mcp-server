"""야구 전용 핸들러 함수."""
import logging
from typing import Any, Dict, List

from server.handlers._common import safe_int, get_team_logo_url, build_recent_games

logger = logging.getLogger(__name__)


def _calc_rate(numerator: int, denominator: int, decimals: int = 3) -> str:
  """원시 카운트에서 비율 계산. 분모 0이면 .000 반환."""
  if denominator <= 0:
    return f"0.{'0' * decimals}"
  return f"{numerator / denominator:.{decimals}f}"


_ZERO_RATE_3 = {"0.000", ".000", "0", ""}
_ZERO_RATE_2 = {"0.00", "0", ""}


def _resolve_batter_avg(b: Dict[str, Any]) -> str:
  api_val = str(b.get("hra_rt", ".000"))
  if api_val not in _ZERO_RATE_3:
    return api_val
  ab = safe_int(b.get("ab_cn"))
  hits = safe_int(b.get("hit_cn"))
  return _calc_rate(hits, ab) if ab > 0 else "0.000"


def _resolve_batter_obp(b: Dict[str, Any]) -> str:
  api_val = str(b.get("obp_rt", ".000"))
  if api_val not in _ZERO_RATE_3:
    return api_val
  ab = safe_int(b.get("ab_cn"))
  hits = safe_int(b.get("hit_cn"))
  walks = safe_int(b.get("bb_cn"))
  return _calc_rate(hits + walks, ab + walks) if ab > 0 else "0.000"


def _resolve_batter_ops(b: Dict[str, Any]) -> str:
  api_val = b.get("ops_rt") or ".000"  # None/falsy → ".000" → _ZERO_RATE_3 → "-"
  if str(api_val) not in _ZERO_RATE_3:
    return str(api_val)
  return "-"


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
  """야구 타자 스탯 빌드. player_id로 중복 제거 (API가 타석별로 중복 반환)."""
  seen: Dict[str, Dict[str, Any]] = {}
  for b in batters:
    player_id = b.get("player_id") or b.get("player_name", "")
    seen[player_id] = {
      "batOrder": safe_int(b.get("bat_order_no")),
      "name": b.get("player_name", "Unknown"),
      "position": b.get("pos_sc") or b.get("position", "-"),
      "atBats": safe_int(b.get("ab_cn")),
      "hits": safe_int(b.get("hit_cn")),
      "homeRuns": safe_int(b.get("hr_cn")),
      "rbi": safe_int(b.get("rbi_cn")),
      "walks": safe_int(b.get("bb_cn")),
      "strikeouts": safe_int(b.get("kk_cn")),
      "avg": _resolve_batter_avg(b),
      "obp": _resolve_batter_obp(b),
      "ops": _resolve_batter_ops(b),
    }
  return sorted(seen.values(), key=lambda x: x["batOrder"])


def _resolve_pitcher_era(p: Dict[str, Any]) -> str:
  """ERA 반환. API 응답값 그대로 사용, 없거나 0이면 "-"."""
  api_val = p.get("era_rt")
  if not api_val or str(api_val) in _ZERO_RATE_2:
    return "-"
  return str(api_val)


def _resolve_pitcher_whip(p: Dict[str, Any]) -> str:
  api_val = p.get("whip_rt")
  if not api_val:
    return "-"
  val_str = str(api_val)
  return "-" if val_str in _ZERO_RATE_2 else val_str


def _build_baseball_pitchers(
  pitchers: List[Dict[str, Any]], starter_id: str = ""
) -> List[Dict[str, Any]]:
  """야구 투수 스탯 빌드. player_id로 중복 제거 (API가 이닝별로 중복 반환).

  Args:
    pitchers: Raw pitcher data from API
    starter_id: Starting pitcher player_id to mark as isStarter=True
  """
  seen: Dict[str, Dict[str, Any]] = {}
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

    player_id = p.get("player_id") or p.get("player_name", "")
    seen[player_id] = {
      "turnNo": safe_int(p.get("turn_no")),
      "name": p.get("player_name", "Unknown"),
      "isStarter": bool(starter_id and player_id == starter_id),
      "result": result_str,
      "innings": str(p.get("pitch_inning", "0")),
      "pitchCount": safe_int(p.get("pit_cn")),
      "hits": safe_int(p.get("hit_cn")),
      "strikeouts": safe_int(p.get("kk_cn")),
      "runs": safe_int(p.get("r_cn")),
      "earnedRuns": safe_int(p.get("er_cn")),
      "era": _resolve_pitcher_era(p),
      "whip": _resolve_pitcher_whip(p),
    }
  # 선발투수 맨 위, 나머지는 turnNo 순
  return sorted(seen.values(), key=lambda x: (0 if x["isStarter"] else 1, x["turnNo"]))


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

  home_team_name = (
    game_info.get("home_team_name")
    or total_info.get("homeTeamInfo", {}).get("home_team_name")
    or "홈팀"
  )
  away_team_name = (
    game_info.get("away_team_name")
    or total_info.get("awayTeamInfo", {}).get("away_team_name")
    or "원정팀"
  )

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
  home_starter_id = game_info.get("home_starter_id", "")
  away_starter_id = game_info.get("away_starter_id", "")

  # Inning scores (shared between home and away teams)
  inning_scores = _build_inning_scores(inning_scores_raw)

  # Batter/pitcher lists
  home_batters = _build_baseball_batters(batter_stat.get("home", []))
  away_batters = _build_baseball_batters(batter_stat.get("away", []))
  home_pitchers = _build_baseball_pitchers(pitcher_stat.get("home", []), home_starter_id)
  away_pitchers = _build_baseball_pitchers(pitcher_stat.get("away", []), away_starter_id)

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

  # League normalization: API name → fallback to ID lookup → default
  league_name = (game_info.get("league_name") or "").strip()
  if not league_name:
    league_id = str(game_info.get("league_id", ""))
    id_to_name = {v: k for k, v in client.get_league_id_map().items()}
    league_name = id_to_name.get(league_id, "KBO리그")
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
