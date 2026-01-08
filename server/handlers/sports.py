"""스포츠 데이터 핸들러."""
import logging
from datetime import datetime
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

    # Calculate scores from player stats if finished (basketball only)
    # For other sports, use scores from game data directly
    home_score = basic_info["home_score"]
    away_score = basic_info["away_score"]
    sport_type = client.get_sport_name()
    if sport_type == "basketball" and basic_info["status"] == "종료" and player_stats:
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
) -> tuple:
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


def _build_basketball_player_data(player: Dict[str, Any]) -> Dict[str, Any]:
    """농구 선수 개별 데이터 생성."""
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

    return {
        "number": safe_int(player.get("back_no"), 0),
        "name": player.get("player_name", "Unknown"),
        "position": player.get("pos_sc", "-"),
        "minutes": minutes,
        "points": safe_int(player.get("tot_score"), 0),
        "rebounds": safe_int(player.get("treb_cn"), 0),
        "assists": safe_int(player.get("assist_cn"), 0),
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


def _calc_percentage(numerator: Any, denominator: Any) -> str:
    """백분율 계산 (문자열 반환).

    Args:
        numerator: 분자
        denominator: 분모

    Returns:
        백분율 문자열 (예: "75.0%") 또는 "-"
    """
    num = safe_int(numerator, 0)
    denom = safe_int(denominator, 0)
    if denom == 0:
        return "-"
    return f"{round(num / denom * 100, 1)}%"


# Sport code mapping
SPORT_CODE_MAP = {
    "soccer": 1,
    "baseball": 2,
    "basketball": 3,
    "volleyball": 4,
    # Numeric codes also supported
    1: 1,
    2: 2,
    3: 3,
    4: 4,
}

SPORT_NAME_MAP = {
    1: "축구",
    2: "야구",
    3: "농구",
    4: "배구",
}


async def get_league_list_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """스포츠별 리그 목록을 조회하는 핸들러.

    Args:
        arguments: 요청 파라미터
            - sport: 스포츠 종류 (soccer, baseball, basketball, volleyball 또는 1-4)

    Returns:
        리그 목록 딕셔너리

    Raises:
        ValueError: 잘못된 스포츠 종류
    """
    import httpx
    from server.config import CONFIG

    sport_input = arguments.get("sport", "basketball")

    # Convert sport name to code
    if isinstance(sport_input, str):
        sport_input = sport_input.lower().strip()

    sport_code = SPORT_CODE_MAP.get(sport_input)
    if sport_code is None:
        valid_sports = list(SPORT_CODE_MAP.keys())
        raise ValueError(
            f"Invalid sport: {sport_input}. Valid options: {valid_sports}"
        )

    sport_name = SPORT_NAME_MAP.get(sport_code, "Unknown")

    # API 호출
    url = f"{CONFIG.sports_api_base_url}/data3V1/livescore/leagueList"
    params = {
        "auth_key": CONFIG.sports_api_key,
        "compe": sport_code,
        "fmt": "json",
    }

    logger.info(f"Fetching league list for {sport_name} (code={sport_code})")

    try:
        async with httpx.AsyncClient(timeout=CONFIG.sports_api_timeout_s) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        # Parse response
        leagues_data = data.get("Data", {}).get("list", [])

        leagues = []
        for league in leagues_data:
            leagues.append({
                "league_id": league.get("LEAGUE_ID", ""),
                "name": league.get("NAME", ""),
                "full_name": league.get("FULL_NAME") or league.get("NAME", ""),
                "category": league.get("COMPE_NAME", ""),
                "category_code": league.get("COMPE", ""),
                "country_code": league.get("COUNTRY_CODE", ""),
                "has_games": league.get("GAME_YN", "-") == "Y",
            })

        logger.info(f"Found {len(leagues)} leagues for {sport_name}")

        return {
            "sport": sport_name,
            "sport_code": sport_code,
            "total_count": len(leagues),
            "leagues": leagues,
        }

    except httpx.TimeoutException:
        logger.error(f"Timeout fetching league list for {sport_name}")
        raise ValueError(f"API timeout while fetching {sport_name} leagues")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching league list: {e.response.status_code}")
        raise ValueError(f"API error: {e.response.status_code}")

    except Exception as e:
        logger.error(f"Failed to fetch league list: {e}")
        raise ValueError(f"Failed to fetch league list: {e}")
