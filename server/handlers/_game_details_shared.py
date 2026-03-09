"""공통 게임 상세 보조 함수."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from server.services.sports.base.client import BaseSportsClient
from server.services.sports.base.mapper import BaseResponseMapper
from server.services.cache import cache_games, find_game_in_cache
from server.handlers._common import safe_int, safe_float, get_team_logo_url, build_recent_games
from server.handlers.soccer import _build_soccer_player_data
from server.handlers.basketball import _build_basketball_player_data
from server.handlers.volleyball import _build_volleyball_player_data

logger = logging.getLogger(__name__)


async def _get_game_info(
  client: BaseSportsClient, game_id: str, date_param: str, sport: str
) -> Optional[Dict[str, Any]]:
  """게임 정보 조회 (캐시 또는 API)."""
  game_info = None

  if client.use_mock:
    # Mock mode: 스포츠별 mock data 사용
    mock_games = {}
    if sport == "basketball":
      from server.services.sports.basketball.mock_data import MOCK_BASKETBALL_GAMES
      mock_games = MOCK_BASKETBALL_GAMES
    elif sport == "soccer":
      from server.services.sports.soccer.mock_data import MOCK_SOCCER_GAMES
      mock_games = MOCK_SOCCER_GAMES

    for games in mock_games.values():
      for game in games:
        if game["game_id"] == game_id:
          game_info = game
          break
      if game_info:
        break

    if not game_info:
      raise ValueError(f"Game {game_id} not found in {sport} mock data")
  else:
    # Real API mode
    if date_param:
      game_info = find_game_in_cache(date_param, sport, game_id)

    if not game_info and date_param:
      try:
        games = await client.get_games_by_sport(date_param)
        if games:
          cache_games(date_param, sport, games)
        for game in games:
          if game.get("game_id") == game_id:
            game_info = game
            break
      except Exception as e:
        logger.warning(f"Failed to get game info from games API: {e}")

  return game_info


def _extract_basic_info(
  client: BaseSportsClient, game_info: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
  """게임 정보에서 기본 정보 추출."""
  default_league = client.get_default_league() or "Unknown"
  league_id_map = client.get_league_id_map()

  info = {
    "home_team_name": "Home",
    "away_team_name": "Away",
    "home_team_id": "",
    "away_team_id": "",
    "league": default_league,
    "league_id": "",
    "formatted_date": "",
    "match_time": "",
    "status": "종료",
    "home_score": 0,
    "away_score": 0,
    "venue": "",
  }

  if game_info:
    match_date = game_info.get("match_date", "")
    info["formatted_date"] = f"{match_date[4:6]}.{match_date[6:8]}" if len(match_date) >= 8 else ""
    info["match_time"] = game_info.get("match_time", "")

    state_raw = game_info.get("state", "").upper()
    state_map = {"F": "종료", "I": "진행중", "B": "예정"}
    info["status"] = state_map.get(state_raw, "종료")

    info["league"] = game_info.get("league_name", default_league)
    info["league_id"] = game_info.get("league_id", "")

    # Fallback: derive league_id from league_name
    if not info["league_id"]:
      info["league_id"] = league_id_map.get(info["league"], "")

    info["home_team_name"] = game_info.get("home_team_name", "Home")
    info["home_team_id"] = game_info.get("home_team_id", "")
    info["away_team_name"] = game_info.get("away_team_name", "Away")
    info["away_team_id"] = game_info.get("away_team_id", "")
    info["home_score"] = safe_int(game_info.get("home_score"), 0)
    info["away_score"] = safe_int(game_info.get("away_score"), 0)
    info["venue"] = game_info.get("arena_name", "")

  return info


async def _get_standings_data(
  client: BaseSportsClient, league_id: str, game_info: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
  """순위 데이터 조회."""
  if not client.has_operation("team_rank"):
    return []

  standings: List[Dict[str, Any]] = []
  try:
    season_id = datetime.now().strftime("%Y")
    if game_info:
      match_date = game_info.get("match_date", "")
      if match_date and len(match_date) >= 4:
        season_id = match_date[:4]

    team_rank_data = await client.get_team_rank(season_id=season_id, league_id=league_id)

    if team_rank_data:
      team_name_map = client.get_team_name_map()
      conference_map = client.get_conference_map()
      grouped: Dict[str, List[Dict[str, Any]]] = {}

      for team in team_rank_data:
        group = team.get("group", "")
        conf_name = conference_map.get(group, group)

        if conf_name not in grouped:
          grouped[conf_name] = []

        team_id = team.get("team_id", "")
        team_name = team.get("team_name") or team_name_map.get(team_id, "Unknown")

        grouped[conf_name].append({
          "rank": safe_int(team.get("rank"), 0),
          "name": team_name,
          "shortName": team_name,
          "wins": safe_int(team.get("wins"), 0),
          "losses": safe_int(team.get("losses"), 0),
          "winRate": team.get("win_rate", "0.000"),
          "recentGames": [],
          # Soccer-specific fields (0 for other sports that don't provide them)
          "played": safe_int(team.get("games_played"), 0),
          "draws": safe_int(team.get("draws"), 0),
          "goalsFor": safe_int(team.get("goals_for"), 0),
          "goalsAgainst": safe_int(team.get("goals_against"), 0),
          "goalDifference": safe_int(team.get("goal_diff"), 0),
          "points": safe_int(team.get("points"), 0),
        })

      for conf_name, teams in grouped.items():
        standing_entry: Dict[str, Any] = {
          "teams": sorted(teams, key=lambda x: x["rank"]),
        }
        if conf_name in ["동부", "서부"]:
          standing_entry["conference"] = conf_name
        standings.append(standing_entry)

      logger.debug(f"Retrieved standings: {len(standings)} conferences")
  except Exception as e:
    logger.warning(f"Failed to get team rankings: {e}")

  return standings


async def _get_team_vs_data(
  client: BaseSportsClient,
  game_id: str,
  league_id: str,
  home_team_id: str,
  away_team_id: str,
  game_info: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
  """팀 vs 팀 비교 데이터 조회."""
  result: Dict[str, Any] = {
    "home_record": "",
    "away_record": "",
    "home_recent_games": [],
    "away_recent_games": [],
    "team_comparison": None,
    "head_to_head": None,
  }

  if not client.has_operation("team_vs_list"):
    return result

  try:
    season_id = datetime.now().strftime("%Y")
    if game_info:
      match_date = game_info.get("match_date", "")
      if match_date and len(match_date) >= 4:
        season_id = match_date[:4]

    team_vs_data = await client.get_team_vs_list(
      season_id=season_id,
      league_id=league_id,
      game_id=game_id,
      home_team_id=home_team_id,
      away_team_id=away_team_id,
    )

    if team_vs_data:
      home_wins = safe_int(team_vs_data.get("home_wins"), 0)
      home_losses = safe_int(team_vs_data.get("home_losses"), 0)
      away_wins = safe_int(team_vs_data.get("away_wins"), 0)
      away_losses = safe_int(team_vs_data.get("away_losses"), 0)

      result["home_record"] = f"{home_wins}승 {home_losses}패"
      result["away_record"] = f"{away_wins}승 {away_losses}패"

      home_results_str = team_vs_data.get("home_recent_results", "")
      away_results_str = team_vs_data.get("away_recent_results", "")

      if home_results_str:
        result["home_recent_games"] = [r.strip() for r in home_results_str.split(",") if r.strip()]
      else:
        result["home_recent_games"] = build_recent_games(
          safe_int(team_vs_data.get("home_recent_wins"), 0),
          safe_int(team_vs_data.get("home_recent_losses"), 0),
        )

      if away_results_str:
        result["away_recent_games"] = [r.strip() for r in away_results_str.split(",") if r.strip()]
      else:
        result["away_recent_games"] = build_recent_games(
          safe_int(team_vs_data.get("away_recent_wins"), 0),
          safe_int(team_vs_data.get("away_recent_losses"), 0),
        )

      result["team_comparison"] = {
        "home": {
          "winRate": str(team_vs_data.get("home_win_rate", "0")),
          "avgPoints": safe_float(team_vs_data.get("home_avg_points")),
          "avgPointsAgainst": safe_float(team_vs_data.get("home_avg_points_against")),
          "fgPct": str(team_vs_data.get("home_fg_pct", "0")),
          "threePct": str(team_vs_data.get("home_3p_pct", "0")),
          "avgRebounds": safe_float(team_vs_data.get("home_avg_rebounds")),
          "avgAssists": safe_float(team_vs_data.get("home_avg_assists")),
          "avgSteals": safe_float(team_vs_data.get("home_avg_steals")),
          "avgBlocks": safe_float(team_vs_data.get("home_avg_blocks")),
          "avgTurnovers": safe_float(team_vs_data.get("home_avg_turnovers")),
        },
        "away": {
          "winRate": str(team_vs_data.get("away_win_rate", "0")),
          "avgPoints": safe_float(team_vs_data.get("away_avg_points")),
          "avgPointsAgainst": safe_float(team_vs_data.get("away_avg_points_against")),
          "fgPct": str(team_vs_data.get("away_fg_pct", "0")),
          "threePct": str(team_vs_data.get("away_3p_pct", "0")),
          "avgRebounds": safe_float(team_vs_data.get("away_avg_rebounds")),
          "avgAssists": safe_float(team_vs_data.get("away_avg_assists")),
          "avgSteals": safe_float(team_vs_data.get("away_avg_steals")),
          "avgBlocks": safe_float(team_vs_data.get("away_avg_blocks")),
          "avgTurnovers": safe_float(team_vs_data.get("away_avg_turnovers")),
        },
      }

      # 축구 상대전적 (head-to-head) 빌드
      # mock 데이터: home_team_vs_w_cn, real API (mapped): home_h2h_wins
      home_h2h_wins = safe_int(
        team_vs_data.get("home_h2h_wins") or team_vs_data.get("home_team_vs_w_cn"), 0
      )
      home_h2h_draws = safe_int(
        team_vs_data.get("home_h2h_draws") or team_vs_data.get("home_team_vs_d_cn"), 0
      )
      home_h2h_losses = safe_int(
        team_vs_data.get("home_h2h_losses") or team_vs_data.get("home_team_vs_l_cn"), 0
      )
      away_h2h_wins = safe_int(
        team_vs_data.get("away_h2h_wins") or team_vs_data.get("away_team_vs_w_cn"), 0
      )

      total_h2h_games = home_h2h_wins + home_h2h_draws + home_h2h_losses

      if total_h2h_games > 0:
        result["head_to_head"] = {
          "totalGames": total_h2h_games,
          "homeWins": home_h2h_wins,
          "awayWins": away_h2h_wins,
          "draws": home_h2h_draws,
        }

      logger.debug(f"Team vs data: home={result['home_record']}, away={result['away_record']}")
  except Exception as e:
    logger.warning(f"Failed to get team vs list: {e}")

  return result


async def _get_lineup_data(
  client: BaseSportsClient, mapper: BaseResponseMapper, game_id: str, team_id: str
) -> List[Dict[str, Any]]:
  """라인업 데이터 조회."""
  if not client.has_operation("lineup") or not team_id:
    return []

  lineup: List[Dict[str, Any]] = []
  try:
    lineup_data = await client.get_lineup(game_id, team_id)

    if lineup_data:
      position_map = mapper.get_position_map()
      starter_positions = mapper.get_starter_positions()

      for player in lineup_data:
        pos_no = str(player.get("pos_no", "5"))
        position = position_map.get(pos_no, "BENCH")
        is_starter = pos_no in starter_positions

        lineup.append({
          "playerId": player.get("player_id", ""),
          "name": player.get("player_name", "Unknown"),
          "number": safe_int(player.get("back_no"), 0),
          "position": position,
          "isStarter": is_starter,
        })

      logger.debug(f"Retrieved lineup for team {team_id}: {len(lineup)} players")
  except Exception as e:
    logger.warning(f"Failed to get lineup for team {team_id}: {e}")

  return lineup


async def _build_scheduled_game_response(
  client: BaseSportsClient,
  mapper: BaseResponseMapper,
  game_id: str,
  basic_info: Dict[str, Any],
  game_info: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
  """예정된 경기 응답 생성."""
  logger.info(f"[get_game_details_handler] Returning schedule for {basic_info['home_team_name']} vs {basic_info['away_team_name']}")

  standings = await _get_standings_data(client, basic_info["league_id"], game_info)
  vs_data = await _get_team_vs_data(
    client, game_id, basic_info["league_id"],
    basic_info["home_team_id"], basic_info["away_team_id"], game_info
  )

  home_lineup = await _get_lineup_data(client, mapper, game_id, basic_info["home_team_id"])
  away_lineup = await _get_lineup_data(client, mapper, game_id, basic_info["away_team_id"])

  sport_type = client.get_sport_name()

  result: Dict[str, Any] = {
    "sportType": sport_type,
    "league": basic_info["league"],
    "date": basic_info["formatted_date"],
    "status": basic_info["status"],
    "time": basic_info["match_time"],
    "homeTeam": {
      "name": basic_info["home_team_name"],
      "shortName": basic_info["home_team_name"],
      "logo": get_team_logo_url(basic_info["home_team_id"]),
      "record": vs_data["home_record"],
      "score": 0,
      "players": [],
      "recentGames": vs_data["home_recent_games"],
    },
    "awayTeam": {
      "name": basic_info["away_team_name"],
      "shortName": basic_info["away_team_name"],
      "logo": get_team_logo_url(basic_info["away_team_id"]),
      "record": vs_data["away_record"],
      "score": 0,
      "players": [],
      "recentGames": vs_data["away_recent_games"],
    },
    "gameRecords": [],
  }

  if sport_type == "volleyball":
    result["homeTeam"]["setsWon"] = 0
    result["homeTeam"]["primaryColor"] = "#003DA5"
    result["homeTeam"]["secondaryColor"] = "#FFFFFF"
    result["awayTeam"]["setsWon"] = 0
    result["awayTeam"]["primaryColor"] = "#1f2937"
    result["awayTeam"]["secondaryColor"] = "#FFFFFF"

  if home_lineup:
    result["homeTeam"]["lineup"] = home_lineup
  if away_lineup:
    result["awayTeam"]["lineup"] = away_lineup
  if basic_info["venue"]:
    result["venue"] = basic_info["venue"]
  if standings:
    result["standings"] = standings
  if vs_data["team_comparison"]:
    result["teamComparison"] = vs_data["team_comparison"]
  if vs_data["head_to_head"]:
    result["headToHead"] = vs_data["head_to_head"]

  return result


async def _build_live_or_finished_game_response(
  client: BaseSportsClient,
  mapper: BaseResponseMapper,
  game_id: str,
  basic_info: Dict[str, Any],
  game_info: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
  """진행중 또는 종료된 경기 응답 생성."""
  # Get team stats (may be empty for some leagues like KBL D리그)
  team_stats = await client.get_team_stats(game_id)
  has_team_stats = team_stats and len(team_stats) >= 2

  if not has_team_stats:
    logger.warning(
      f"[get_game_details] No team stats for game {game_id} "
      f"(league={basic_info['league']}). Showing basic score only."
    )

  # Extract team stats if available, otherwise use empty dicts
  home_stats = team_stats[0] if has_team_stats else {}
  away_stats = team_stats[1] if has_team_stats else {}

  # Update team IDs if not set (prefer basic_info, fallback to team_stats)
  home_team_id = basic_info["home_team_id"] or home_stats.get("home_team_id", "")
  away_team_id = basic_info["away_team_id"] or away_stats.get("away_team_id", "")

  # Get player stats (only if team stats are available)
  player_stats = []
  if has_team_stats:
    try:
      player_stats = await client.get_player_stats(game_id, home_team_id, away_team_id) or []
    except Exception as e:
      logger.warning(f"[WARN] Player stats not available for game {game_id}: {e}")

  # Use scores from basic_info (game list) as the primary source
  home_score = basic_info["home_score"]
  away_score = basic_info["away_score"]
  sport_type = client.get_sport_name()

  # For basketball with player stats, calculate from player data for accuracy
  if sport_type == "basketball" and basic_info["status"] == "종료" and player_stats:
    calculated_home = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == home_team_id)
    calculated_away = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == away_team_id)
    # Only use calculated scores if they're non-zero
    if calculated_home > 0 or calculated_away > 0:
      home_score = calculated_home
      away_score = calculated_away

  # Get additional data
  vs_data = await _get_team_vs_data(
    client, game_id, basic_info["league_id"],
    home_team_id, away_team_id, game_info
  )
  standings = await _get_standings_data(client, basic_info["league_id"], game_info)
  home_lineup = await _get_lineup_data(client, mapper, game_id, home_team_id)
  away_lineup = await _get_lineup_data(client, mapper, game_id, away_team_id)

  # Build player lists (스포츠 타입에 따라 다른 포맷 사용)
  sport_type = client.get_sport_name()

  # 축구의 경우 lineup에서 선수 이름/등번호를 가져와야 함
  lineup_map: Dict[str, Dict[str, Any]] = {}
  if sport_type == "soccer":
    for player in home_lineup + away_lineup:
      player_id = player.get("playerId", "")
      if player_id:
        lineup_map[player_id] = {
          "name": player.get("name", ""),
          "number": player.get("number", 0),
        }

  home_players, away_players = _build_player_lists(
    player_stats, home_team_id, away_team_id, sport_type, lineup_map
  )

  # Build game records using mapper (empty if no team stats)
  game_records = mapper.build_game_records(home_stats, away_stats) if has_team_stats else []

  result: Dict[str, Any] = {
    "sportType": sport_type,
    "league": basic_info["league"],
    "date": basic_info["formatted_date"],
    "status": basic_info["status"],
    "homeTeam": {
      "name": basic_info["home_team_name"],
      "shortName": basic_info["home_team_name"],
      "logo": get_team_logo_url(home_team_id),
      "record": vs_data["home_record"],
      "score": home_score,
      "players": home_players,
      "recentGames": vs_data["home_recent_games"],
    },
    "awayTeam": {
      "name": basic_info["away_team_name"],
      "shortName": basic_info["away_team_name"],
      "logo": get_team_logo_url(away_team_id),
      "record": vs_data["away_record"],
      "score": away_score,
      "players": away_players,
      "recentGames": vs_data["away_recent_games"],
    },
    "gameRecords": game_records,
  }

  if sport_type == "soccer" and has_team_stats:
    home_fhg = safe_int(home_stats.get("first_half_goals"), 0)
    away_fhg = safe_int(away_stats.get("first_half_goals"), 0)
    result["homeTeam"]["halfScores"] = {
      "firstHalf": home_fhg,
      "secondHalf": home_score - home_fhg,
    }
    result["awayTeam"]["halfScores"] = {
      "firstHalf": away_fhg,
      "secondHalf": away_score - away_fhg,
    }

  if sport_type == "volleyball":
    result["homeTeam"]["setsWon"] = home_score
    result["homeTeam"]["primaryColor"] = "#003DA5"
    result["homeTeam"]["secondaryColor"] = "#FFFFFF"
    result["awayTeam"]["setsWon"] = away_score
    result["awayTeam"]["primaryColor"] = "#1f2937"
    result["awayTeam"]["secondaryColor"] = "#FFFFFF"

  if basic_info["venue"]:
    result["venue"] = basic_info["venue"]
  if basic_info["match_time"]:
    result["time"] = basic_info["match_time"]
  if standings:
    result["standings"] = standings
  if vs_data["team_comparison"]:
    result["teamComparison"] = vs_data["team_comparison"]
  if vs_data["head_to_head"]:
    result["headToHead"] = vs_data["head_to_head"]
  if home_lineup:
    result["homeTeam"]["lineup"] = home_lineup
  if away_lineup:
    result["awayTeam"]["lineup"] = away_lineup

  logger.info(f"[get_game_details_handler] Returning data for {basic_info['home_team_name']} vs {basic_info['away_team_name']}")

  return result


def _build_player_lists(
  player_stats: List[Dict[str, Any]],
  home_team_id: str,
  away_team_id: str,
  sport_type: str = "basketball",
  lineup_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[List, List]:
  """선수 통계를 홈/어웨이 리스트로 분리.

  Args:
    player_stats: 선수 통계 리스트
    home_team_id: 홈팀 ID
    away_team_id: 원정팀 ID
    sport_type: 스포츠 종류 (soccer, basketball, etc.)
    lineup_map: 축구용 선수 정보 매핑 {player_id: {name, number}}

  Returns:
    (home_players, away_players) 튜플
  """
  home_players = []
  away_players = []

  for player in player_stats:
    # API 응답은 대문자(TEAM_ID), 매핑 후는 소문자(team_id)
    player_team_id = player.get("team_id") or player.get("TEAM_ID", "")

    # 스포츠별 빌더 함수 호출
    if sport_type == "soccer":
      player_data = _build_soccer_player_data(player, lineup_map)
    elif sport_type == "volleyball":
      player_data = _build_volleyball_player_data(player)
    else:
      player_data = _build_basketball_player_data(player)

    if player_team_id == home_team_id:
      home_players.append(player_data)
    elif player_team_id == away_team_id:
      away_players.append(player_data)

  # 출전 시간 기준 내림차순 정렬
  home_players.sort(key=lambda x: x.get("minutes", 0), reverse=True)
  away_players.sort(key=lambda x: x.get("minutes", 0), reverse=True)

  return home_players, away_players
