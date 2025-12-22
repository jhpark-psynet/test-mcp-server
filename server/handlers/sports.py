"""스포츠 데이터 핸들러."""
import logging
from typing import Any, Dict, List, Optional, Union

from server.services.sports import SportsClientFactory
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
    """팀 로고 URL 생성.

    Args:
        team_id: 팀 ID

    Returns:
        팀 로고 URL
    """
    if not team_id:
        return ""
    return TEAM_LOGO_URL_TEMPLATE.format(team_id=team_id)


def build_recent_games(wins: int, losses: int) -> List[str]:
    """최근 5경기 결과 배열 생성 (승리 먼저, 패배 나중).

    Args:
        wins: 최근 5경기 중 승리 수
        losses: 최근 5경기 중 패배 수

    Returns:
        ['W', 'W', 'L', ...] 형태의 배열
    """
    total = wins + losses
    if total == 0:
        return []
    # 최근 경기 순서는 알 수 없으므로 승리를 먼저 배치
    return ['W'] * wins + ['L'] * losses


def safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """안전하게 int로 변환. 빈 문자열, None, 공백 등을 처리.

    Args:
        value: 변환할 값
        default: 변환 실패 시 반환할 기본값

    Returns:
        변환된 정수값 또는 기본값
    """
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


from server.services.sports.basketball.mock_data import MOCK_BASKETBALL_GAMES as MOCK_GAMES_DB


def _format_games_response(games: List[Dict[str, Any]], sport: str, date: str) -> str:
    """게임 목록을 포맷팅된 문자열로 변환.

    Args:
        games: 게임 목록
        sport: 스포츠 종류
        date: 날짜

    Returns:
        포맷팅된 응답 문자열
    """
    # Format games by league
    leagues: Dict[str, list] = {}
    for game in games:
        league = game.get("league_name", "Unknown")
        if league not in leagues:
            leagues[league] = []
        leagues[league].append(game)

    # Build formatted response
    lines = [f"## {sport.capitalize()} Games on {date}\n"]

    for league, league_games in leagues.items():
        lines.append(f"### [{league}]")

        for game in league_games:
            home = game.get("home_team_name", "Unknown")
            away = game.get("away_team_name", "Unknown")
            time = game.get("match_time", "")
            state = game.get("state", "")
            arena = game.get("arena_name", "")

            if state.upper() == "F":  # Finished
                home_score = game.get("home_score", 0)
                away_score = game.get("away_score", 0)
                result = "W" if home_score > away_score else "L" if home_score < away_score else "D"
                lines.append(
                    f"- **{home}** {home_score} - {away_score} **{away}** (Finished, {result})"
                )
            else:  # Before game
                lines.append(
                    f"- **{home}** vs **{away}** ({time}, Scheduled)"
                )

            if arena:
                lines.append(f"  - Arena: {arena}")
            lines.append(f"  - Game ID: `{game.get('game_id', '')}`")
            lines.append("")

    return "\n".join(lines)


async def get_games_by_sport_handler(arguments: Dict[str, Any]) -> str:
    """특정 날짜의 스포츠 경기 목록을 조회하는 핸들러.

    Args:
        arguments: Tool arguments with 'date', 'sport', and optional 'force_refresh' fields

    Returns:
        Formatted game list

    Raises:
        ValueError: Invalid input parameters
        Exception: Other errors during processing
    """
    date = arguments.get("date", "")
    sport = arguments.get("sport", "")
    force_refresh = arguments.get("force_refresh", False)

    # Let exceptions bubble up so server_factory can set isError=True
    client = SportsClientFactory.create_client(sport)

    # 실제 API 모드에서만 캐시 로직 적용
    if not client.use_mock:
        # force_refresh 시 기존 캐시 무효화
        if force_refresh:
            invalidate_cache(date, sport)
            logger.info(f"Force refresh requested for {date}_{sport}")
        else:
            # 캐시에서 먼저 조회
            cached_games = get_cached_games(date, sport)
            if cached_games:
                # 캐시된 데이터로 응답 포맷팅
                return _format_games_response(cached_games, sport, date)

    # API 호출
    games = await client.get_games_by_sport(date)

    # 실제 API 모드에서 유효한 데이터만 캐시 저장
    if not client.use_mock and games:
        cache_games(date, sport, games)

    if not games:
        return f"No {sport} games found on {date}"

    return _format_games_response(games, sport, date)


async def get_game_details_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """경기의 상세 정보 (팀 통계 + 선수 통계)를 조회하는 핸들러 (위젯용).

    Args:
        arguments: Tool arguments with 'game_id' and 'sport' fields

    Returns:
        GameData format for game-result-viewer widget

    Raises:
        ValueError: Game not found or game not finished
        Exception: Other errors during processing
    """
    game_id = arguments.get("game_id", "").strip()
    sport = arguments.get("sport", "basketball").strip()
    date_param = arguments.get("date", "").strip()

    # Create sport-specific client
    client = SportsClientFactory.create_client(sport)

    # Get game info first (from mock DB or real API)
    game_info = None

    if client.use_mock:
        for games in MOCK_GAMES_DB.values():
            for game in games:
                if game["game_id"] == game_id:
                    game_info = game
                    break
            if game_info:
                break

        if not game_info:
            raise ValueError(f"Game {game_id} not found in mock data")
    else:
        # Real API mode: 캐시에서 먼저 조회
        if date_param:
            game_info = find_game_in_cache(date_param, sport, game_id)

        # 캐시 미스 시 API 호출
        if not game_info and date_param:
            try:
                games = await client.get_games_by_sport(date_param)
                # 유효한 데이터만 캐시에 저장
                if games:
                    cache_games(date_param, sport, games)

                for game in games:
                    if game.get("game_id") == game_id:
                        game_info = game
                        break
            except Exception as e:
                logger.warning(f"Failed to get game info from games API: {e}")

    # Extract basic game info
    home_team_name = "Home"
    away_team_name = "Away"
    home_team_id = ""
    away_team_id = ""
    league = "NBA"
    league_id = ""
    formatted_date = ""
    match_time = ""
    status = "종료"
    home_score = 0
    away_score = 0
    venue = ""

    if game_info:
        match_date = game_info.get("match_date", "")
        formatted_date = f"{match_date[4:6]}.{match_date[6:8]}" if len(match_date) >= 8 else ""
        match_time = game_info.get("match_time", "")
        state_raw = game_info.get("state", "").upper()
        state_map = {"F": "종료", "I": "진행중", "B": "예정"}
        status = state_map.get(state_raw, "종료")
        league = game_info.get("league_name", "NBA")
        league_id = game_info.get("league_id", "")
        # Fallback: derive league_id from league_name if not provided
        if not league_id:
            league_id_map = {
                "NBA": "OT313",
                "KBL": "KBL",
                "WKBL": "WKBL",
            }
            league_id = league_id_map.get(league, "")
        home_team_name = game_info.get("home_team_name", "Home")
        home_team_id = game_info.get("home_team_id", "")
        away_team_name = game_info.get("away_team_name", "Away")
        away_team_id = game_info.get("away_team_id", "")
        home_score = safe_int(game_info.get("home_score"), 0)
        away_score = safe_int(game_info.get("away_score"), 0)
        venue = game_info.get("arena_name", "")
        logger.debug(f"Found game info: {home_team_name} vs {away_team_name}, status={status}, venue={venue}")

    # Helper function to get standings
    async def get_standings_data() -> List[Dict[str, Any]]:
        """Get team rankings and convert to frontend format."""
        standings: List[Dict[str, Any]] = []
        try:
            season_for_rank = "2025"
            if game_info:
                season_for_rank = game_info.get("match_date", "2025")[:4]

            team_rank_data = await client.get_team_rank(
                season_id=season_for_rank,
                league_id=league_id,
            )

            if team_rank_data:
                # Debug: log first team's keys to see available fields
                if team_rank_data:
                    logger.debug(f"Team rank data keys: {list(team_rank_data[0].keys())}")
                    logger.debug(f"First team data: {team_rank_data[0]}")

                conference_map = {"EAST": "동부", "WEST": "서부"}
                grouped: Dict[str, List[Dict[str, Any]]] = {}

                # Team ID to team name mapping (Real API doesn't return team_name)
                team_names = {
                    # NBA - Eastern Conference
                    "OT31237": "클리블랜드", "OT31264": "인디애나", "OT31246": "보스턴",
                    "OT31240": "올랜도", "OT31238": "밀워키", "OT31263": "뉴욕닉스",
                    "OT31241": "디트로이트", "OT31265": "브루클린", "OT31266": "마이애미",
                    "OT31267": "필라델피아", "OT31243": "시카고", "OT31239": "토론토",
                    "OT31244": "애틀랜타", "OT31261": "샬렛", "OT31262": "워싱턴",
                    # NBA - Western Conference
                    "OT31255": "오클라호마시티", "OT31257": "멤피스", "OT31252": "휴스턴",
                    "OT31254": "LA레이커스", "OT31250": "덴버", "OT31253": "LA클리퍼스",
                    "OT31256": "미네소타", "OT31258": "피닉스", "OT31260": "골든스테이트",
                    "OT31251": "댈러스", "OT31259": "새크라멘토", "OT31245": "샌안토니오",
                    "OT31247": "포틀랜드", "OT31248": "유타", "OT31249": "뉴올리언스",
                    # KBL
                    "3LG": "창원LG", "3SK": "서울SK", "3KT": "수원KT", "3SS": "서울삼성",
                    "3KG": "안양정관장", "3OR": "고양오리온", "3KA": "울산현대모비스",
                    "3DB": "원주DB", "3HN": "대구한국가스공사", "3SN": "소노",
                    # WKBL
                    "3KB": "청주KB스타즈", "3SS": "용인삼성생명", "3HB": "하나원큐",
                    "3BK": "BNK썸", "3SH": "신한은행", "3WB": "우리은행",
                }

                for team in team_rank_data:
                    group = team.get("group", "")
                    conf_name = conference_map.get(group, group)

                    if conf_name not in grouped:
                        grouped[conf_name] = []

                    team_id = team.get("team_id", "")
                    team_name = team.get("team_name") or team_names.get(team_id, "Unknown")

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
                    # Only include conference if it's valid (동부/서부)
                    if conf_name in ["동부", "서부"]:
                        standing_entry["conference"] = conf_name
                    standings.append(standing_entry)

                logger.debug(f"Retrieved standings: {len(standings)} conferences")
        except Exception as e:
            logger.warning(f"Failed to get team rankings: {e}")
        return standings

    # For scheduled games (예정), return early with schedule info only
    if status == "예정":
        logger.info(f"[get_game_details_handler] Returning schedule for {home_team_name} vs {away_team_name}")
        standings = await get_standings_data()
        result: Dict[str, Any] = {
            "sportType": sport,
            "league": league,
            "date": formatted_date,
            "status": status,
            "time": match_time,
            "homeTeam": {
                "name": home_team_name,
                "shortName": home_team_name,
                "logo": get_team_logo_url(home_team_id),
                "record": "",
                "score": 0,
                "players": [],
                "recentGames": [],
            },
            "awayTeam": {
                "name": away_team_name,
                "shortName": away_team_name,
                "logo": get_team_logo_url(away_team_id),
                "record": "",
                "score": 0,
                "players": [],
                "recentGames": [],
            },
            "gameRecords": [],
        }
        if venue:
            result["venue"] = venue
        if standings:
            result["standings"] = standings
        return result

    # Get team stats for started/finished games
    team_stats = await client.get_team_stats(game_id)
    if not team_stats or len(team_stats) < 2:
        raise ValueError(f"Team stats not found for game {game_id}")

    logger.debug(f"team_stats[0] keys: {list(team_stats[0].keys())}")

    # Update team IDs from team_stats if not already set
    if not home_team_id:
        home_team_id = team_stats[0].get("home_team_id", "")
    if not away_team_id:
        away_team_id = team_stats[1].get("away_team_id", "")

    # Get player stats (optional - may not exist for live games)
    try:
        player_stats = await client.get_player_stats(game_id)
    except Exception as e:
        logger.warning(f"[WARN] Player stats not available for game {game_id}: {e}")
        player_stats = []

    # 종료된 경기의 경우 player_stats에서 정확한 점수 계산
    if status == "종료" and player_stats:
        home_score = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == home_team_id)
        away_score = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == away_team_id)

    # Get team vs list for record and recent games
    home_record = ""
    away_record = ""
    home_recent_games: List[str] = []
    away_recent_games: List[str] = []

    try:
        # Extract season from date (e.g., "20251218" -> "2025")
        season_id = formatted_date[:4] if formatted_date else "2025"
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
            # Build record strings
            home_wins = safe_int(team_vs_data.get("home_team_all_w_cn"), 0)
            home_losses = safe_int(team_vs_data.get("home_team_all_l_cn"), 0)
            away_wins = safe_int(team_vs_data.get("away_team_all_w_cn"), 0)
            away_losses = safe_int(team_vs_data.get("away_team_all_l_cn"), 0)

            home_record = f"{home_wins}승 {home_losses}패"
            away_record = f"{away_wins}승 {away_losses}패"

            # Build recent games arrays
            home_recent_wins = safe_int(team_vs_data.get("home_team_5_w_cn"), 0)
            home_recent_losses = safe_int(team_vs_data.get("home_team_5_l_cn"), 0)
            away_recent_wins = safe_int(team_vs_data.get("away_team_5_w_cn"), 0)
            away_recent_losses = safe_int(team_vs_data.get("away_team_5_l_cn"), 0)

            home_recent_games = build_recent_games(home_recent_wins, home_recent_losses)
            away_recent_games = build_recent_games(away_recent_wins, away_recent_losses)

            logger.debug(f"Team vs data: home={home_record}, away={away_record}")
    except Exception as e:
        logger.warning(f"Failed to get team vs list: {e}")

    # Build player lists
    home_players = []
    away_players = []

    for player in player_stats:
        player_team_id = player.get("team_id", "")

        # Parse minutes (HH:MM format -> number)
        player_time = player.get("player_time", "0:00")
        minutes = 0
        try:
            time_parts = player_time.split(":")
            if len(time_parts) >= 2:
                minutes = int(time_parts[0]) * 60 + int(time_parts[1])
                minutes = round(minutes / 60)  # Convert to minutes
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

    # Build game records from team stats
    home_stats = team_stats[0]
    away_stats = team_stats[1]

    home_fgm = safe_int(home_stats.get("home_team_fgm_cn"), 0)
    home_fga = safe_int(home_stats.get("home_team_fga_cn"), 1)
    away_fgm = safe_int(away_stats.get("away_team_fgm_cn"), 0)
    away_fga = safe_int(away_stats.get("away_team_fga_cn"), 1)

    home_3pm = safe_int(home_stats.get("home_team_pgm3_cn"), 0)
    home_3pa = safe_int(home_stats.get("home_team_pga3_cn"), 1)
    away_3pm = safe_int(away_stats.get("away_team_pgm3_cn"), 0)
    away_3pa = safe_int(away_stats.get("away_team_pga3_cn"), 1)

    home_ftm = safe_int(home_stats.get("home_team_ftm_cn"), 0)
    home_fta = safe_int(home_stats.get("home_team_fta_cn"), 1)
    away_ftm = safe_int(away_stats.get("away_team_ftm_cn"), 0)
    away_fta = safe_int(away_stats.get("away_team_fta_cn"), 1)

    home_oreb = safe_int(home_stats.get("home_team_oreb_cn"), 0)
    home_dreb = safe_int(home_stats.get("home_team_dreb_cn"), 0)
    away_oreb = safe_int(away_stats.get("away_team_oreb_cn"), 0)
    away_dreb = safe_int(away_stats.get("away_team_dreb_cn"), 0)

    home_ast = safe_int(home_stats.get("home_team_assist_cn"), 0)
    away_ast = safe_int(away_stats.get("away_team_assist_cn"), 0)

    home_tov = safe_int(home_stats.get("home_team_turnover_cn"), 0)
    away_tov = safe_int(away_stats.get("away_team_turnover_cn"), 0)

    home_stl = safe_int(home_stats.get("home_team_steal_cn"), 0)
    away_stl = safe_int(away_stats.get("away_team_steal_cn"), 0)

    home_blk = safe_int(home_stats.get("home_team_block_cn"), 0)
    away_blk = safe_int(away_stats.get("away_team_block_cn"), 0)

    home_pf = safe_int(home_stats.get("home_team_pfoul_cn"), 0)
    away_pf = safe_int(away_stats.get("away_team_pfoul_cn"), 0)

    game_records = [
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

    # Get team rankings for standings
    standings = await get_standings_data()

    # Return GameData format (must include sportType for component routing)
    result: Dict[str, Any] = {
        "sportType": sport,  # Required for component to select correct viewer
        "league": league,
        "date": formatted_date,
        "status": status,
        "homeTeam": {
            "name": home_team_name,
            "shortName": home_team_name,
            "logo": get_team_logo_url(home_team_id),
            "record": home_record,
            "score": home_score,
            "players": home_players,
            "recentGames": home_recent_games,
        },
        "awayTeam": {
            "name": away_team_name,
            "shortName": away_team_name,
            "logo": get_team_logo_url(away_team_id),
            "record": away_record,
            "score": away_score,
            "players": away_players,
            "recentGames": away_recent_games,
        },
        "gameRecords": game_records,
    }

    # Add venue if available
    if venue:
        result["venue"] = venue

    # Add time field for scheduled games
    if match_time:
        result["time"] = match_time

    # Add standings if available
    if standings:
        result["standings"] = standings

    logger.info(f"[get_game_details_handler] Returning data for {home_team_name} vs {away_team_name}")

    return result
