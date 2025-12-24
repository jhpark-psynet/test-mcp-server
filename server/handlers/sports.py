"""스포츠 데이터 핸들러."""
import logging
from typing import Any, Dict, List, Optional, Union

from server.services.sports import SportsClientFactory
from server.services.sports.base.client import BaseSportsClient
from server.services.sports.base.mapper import BaseResponseMapper
from server.services.cache import (
    cache_games,
    get_cached_games,
    find_game_in_cache,
    invalidate_cache,
)

logger = logging.getLogger(__name__)

# Team logo URL template
TEAM_LOGO_URL_TEMPLATE = "https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_{team_id}.png"


def get_team_logo_url(team_id: str) -> str:
    """팀 로고 URL 생성."""
    if not team_id:
        return ""
    return TEAM_LOGO_URL_TEMPLATE.format(team_id=team_id)


def build_recent_games(wins: int, losses: int) -> List[str]:
    """최근 5경기 결과 배열 생성 (승리 먼저, 패배 나중)."""
    total = wins + losses
    if total == 0:
        return []
    return ['W'] * wins + ['L'] * losses


def safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """안전하게 int로 변환."""
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


def safe_float(value: Any, default: float = 0.0) -> float:
    """안전하게 float로 변환."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _format_games_response(games: List[Dict[str, Any]], sport: str, date: str) -> str:
    """게임 목록을 포맷팅된 문자열로 변환."""
    leagues: Dict[str, list] = {}
    for game in games:
        league = game.get("league_name", "Unknown")
        if league not in leagues:
            leagues[league] = []
        leagues[league].append(game)

    lines = [f"## {sport.capitalize()} Games on {date}\n"]

    for league, league_games in leagues.items():
        lines.append(f"### [{league}]")

        for game in league_games:
            home = game.get("home_team_name", "Unknown")
            away = game.get("away_team_name", "Unknown")
            time = game.get("match_time", "")
            state = game.get("state", "")
            arena = game.get("arena_name", "")

            if state.upper() == "F":
                home_score = game.get("home_score", 0)
                away_score = game.get("away_score", 0)
                result = "W" if home_score > away_score else "L" if home_score < away_score else "D"
                lines.append(f"- **{home}** {home_score} - {away_score} **{away}** (Finished, {result})")
            else:
                lines.append(f"- **{home}** vs **{away}** ({time}, Scheduled)")

            if arena:
                lines.append(f"  - Arena: {arena}")
            lines.append(f"  - Game ID: `{game.get('game_id', '')}`")
            lines.append("")

    return "\n".join(lines)


async def get_games_by_sport_handler(arguments: Dict[str, Any]) -> str:
    """특정 날짜의 스포츠 경기 목록을 조회하는 핸들러."""
    date = arguments.get("date", "")
    sport = arguments.get("sport", "")
    force_refresh = arguments.get("force_refresh", False)

    client = SportsClientFactory.create_client(sport)

    if not client.use_mock:
        if force_refresh:
            invalidate_cache(date, sport)
            logger.info(f"Force refresh requested for {date}_{sport}")
        else:
            cached_games = get_cached_games(date, sport)
            if cached_games:
                return _format_games_response(cached_games, sport, date)

    games = await client.get_games_by_sport(date)

    if not client.use_mock and games:
        cache_games(date, sport, games)

    if not games:
        return f"No {sport} games found on {date}"

    return _format_games_response(games, sport, date)


async def get_game_details_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """경기의 상세 정보를 조회하는 핸들러 (위젯용).

    모든 스포츠에 대응하는 범용 핸들러.
    스포츠별 특화 로직은 client와 mapper에 위임.
    """
    game_id = arguments.get("game_id", "").strip()
    sport = arguments.get("sport", "basketball").strip()
    date_param = arguments.get("date", "").strip()

    # Create sport-specific client
    client = SportsClientFactory.create_client(sport)
    mapper = client.mapper

    # Get game info
    game_info = await _get_game_info(client, game_id, date_param, sport)

    # Extract basic game info
    basic_info = _extract_basic_info(client, game_info)

    # Build response based on game status
    if basic_info["status"] == "예정":
        return await _build_scheduled_game_response(
            client, mapper, game_id, basic_info, game_info
        )
    else:
        return await _build_live_or_finished_game_response(
            client, mapper, game_id, basic_info, game_info
        )


async def _get_game_info(
    client: BaseSportsClient, game_id: str, date_param: str, sport: str
) -> Optional[Dict[str, Any]]:
    """게임 정보 조회 (캐시 또는 API)."""
    game_info = None

    if client.use_mock:
        # Mock mode: basketball mock data만 사용
        from server.services.sports.basketball.mock_data import MOCK_BASKETBALL_GAMES
        for games in MOCK_BASKETBALL_GAMES.values():
            for game in games:
                if game["game_id"] == game_id:
                    game_info = game
                    break
            if game_info:
                break

        if not game_info:
            raise ValueError(f"Game {game_id} not found in mock data")
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
        season_id = "2025"
        if game_info:
            season_id = game_info.get("match_date", "2025")[:4]

        team_rank_data = await client.get_team_rank(season_id=season_id, league_id=league_id)

        if team_rank_data:
            team_name_map = client.get_team_name_map()
            conference_map = {"EAST": "동부", "WEST": "서부"}
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
    }

    if not client.has_operation("team_vs_list"):
        return result

    try:
        season_id = "2025"
        if game_info:
            season_id = game_info.get("match_date", "2025")[:4]

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
            starter_positions = {"21", "22", "23", "24", "25"}

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

    result: Dict[str, Any] = {
        "sportType": client.get_sport_name(),
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

    return result


async def _build_live_or_finished_game_response(
    client: BaseSportsClient,
    mapper: BaseResponseMapper,
    game_id: str,
    basic_info: Dict[str, Any],
    game_info: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """진행중 또는 종료된 경기 응답 생성."""
    # Get team stats
    team_stats = await client.get_team_stats(game_id)
    if not team_stats or len(team_stats) < 2:
        raise ValueError(f"Team stats not found for game {game_id}")

    home_stats = team_stats[0]
    away_stats = team_stats[1]

    # Update team IDs if not set
    home_team_id = basic_info["home_team_id"] or home_stats.get("home_team_id", "")
    away_team_id = basic_info["away_team_id"] or away_stats.get("away_team_id", "")

    # Get player stats
    player_stats = []
    try:
        player_stats = await client.get_player_stats(game_id) or []
    except Exception as e:
        logger.warning(f"[WARN] Player stats not available for game {game_id}: {e}")

    # Calculate scores from player stats if finished
    home_score = basic_info["home_score"]
    away_score = basic_info["away_score"]
    if basic_info["status"] == "종료" and player_stats:
        home_score = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == home_team_id)
        away_score = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == away_team_id)

    # Get additional data
    vs_data = await _get_team_vs_data(
        client, game_id, basic_info["league_id"],
        home_team_id, away_team_id, game_info
    )
    standings = await _get_standings_data(client, basic_info["league_id"], game_info)
    home_lineup = await _get_lineup_data(client, mapper, game_id, home_team_id)
    away_lineup = await _get_lineup_data(client, mapper, game_id, away_team_id)

    # Build player lists
    home_players, away_players = _build_player_lists(player_stats, home_team_id, away_team_id)

    # Build game records using mapper
    game_records = mapper.build_game_records(home_stats, away_stats)

    result: Dict[str, Any] = {
        "sportType": client.get_sport_name(),
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

    if basic_info["venue"]:
        result["venue"] = basic_info["venue"]
    if basic_info["match_time"]:
        result["time"] = basic_info["match_time"]
    if standings:
        result["standings"] = standings
    if vs_data["team_comparison"]:
        result["teamComparison"] = vs_data["team_comparison"]
    if home_lineup:
        result["homeTeam"]["lineup"] = home_lineup
    if away_lineup:
        result["awayTeam"]["lineup"] = away_lineup

    logger.info(f"[get_game_details_handler] Returning data for {basic_info['home_team_name']} vs {basic_info['away_team_name']}")

    return result


def _build_player_lists(
    player_stats: List[Dict[str, Any]], home_team_id: str, away_team_id: str
) -> tuple:
    """선수 통계를 홈/어웨이 리스트로 분리."""
    home_players = []
    away_players = []

    for player in player_stats:
        player_team_id = player.get("team_id", "")

        # Parse minutes
        player_time = player.get("player_time", "0:00")
        minutes = 0
        try:
            time_parts = player_time.split(":")
            if len(time_parts) >= 2:
                minutes = int(time_parts[0]) * 60 + int(time_parts[1])
                minutes = round(minutes / 60)
        except:
            minutes = 0

        player_data = {
            "number": safe_int(player.get("back_no"), 0),
            "name": player.get("player_name", "Unknown"),
            "position": player.get("pos_sc", "-"),
            "minutes": minutes,
            "rebounds": safe_int(player.get("treb_cn"), 0),
            "assists": safe_int(player.get("assist_cn"), 0),
            "points": safe_int(player.get("tot_score"), 0)
        }

        if player_team_id == home_team_id:
            home_players.append(player_data)
        elif player_team_id == away_team_id:
            away_players.append(player_data)

    return home_players, away_players
