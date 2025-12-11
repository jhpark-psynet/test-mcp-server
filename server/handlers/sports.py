"""스포츠 데이터 핸들러."""
from typing import Any, Dict, List, Union

from server.services.sports import SportsClientFactory


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


def get_games_by_sport_handler(arguments: Dict[str, Any]) -> str:
    """특정 날짜의 스포츠 경기 목록을 조회하는 핸들러.

    Args:
        arguments: Tool arguments with 'date' and 'sport' fields

    Returns:
        Formatted game list

    Raises:
        ValueError: Invalid input parameters
        Exception: Other errors during processing
    """
    date = arguments.get("date", "")
    sport = arguments.get("sport", "")

    # Let exceptions bubble up so server_factory can set isError=True
    client = SportsClientFactory.create_client(sport)
    games = client.get_games_by_sport(date)

    if not games:
        return f"No {sport} games found on {date}"

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


def get_game_details_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """경기의 상세 정보 (팀 통계 + 선수 통계)를 조회하는 핸들러 (위젯용).

    Args:
        arguments: Tool arguments with 'game_id' and 'sport' fields

    Returns:
        GameData format for game-result-viewer widget

    Raises:
        ValueError: Game not found or game not finished
        Exception: Other errors during processing
    """
    game_id = arguments.get("game_id", "")
    sport = arguments.get("sport", "basketball")

    # Create sport-specific client
    client = SportsClientFactory.create_client(sport)

    # Get game info from MOCK DB only if mock mode is enabled
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

    # Get team stats
    team_stats = client.get_team_stats(game_id)
    if not team_stats or len(team_stats) < 2:
        raise ValueError(f"Team stats not found for game {game_id}")

    # Extract team IDs from team_stats
    home_team_id = team_stats[0].get("home_team_id", "")
    away_team_id = team_stats[1].get("away_team_id", "")

    # Get player stats
    player_stats = client.get_player_stats(game_id)
    if not player_stats:
        raise ValueError(f"Player stats not found for game {game_id}")

    # Use game_info if available (mock mode), otherwise use defaults
    if game_info:
        match_date = game_info.get("match_date", "")
        formatted_date = f"{match_date[4:6]}.{match_date[6:8]}" if len(match_date) >= 8 else ""
        state_raw = game_info.get("state", "").upper()
        state_map = {"F": "종료", "진행중": "진행중", "B": "예정"}
        status = state_map.get(state_raw, "종료")
        league = game_info.get("league_name", "NBA")
        home_team_name = game_info.get("home_team_name", "Home")
        home_score = safe_int(game_info.get("home_score"), 0)
        away_team_name = game_info.get("away_team_name", "Away")
        away_score = safe_int(game_info.get("away_score"), 0)
    else:
        # Real API mode: game_info not available, use defaults
        formatted_date = ""
        status = "종료"
        league = "NBA"
        home_team_name = "Home"
        away_team_name = "Away"
        # Calculate scores from player stats
        home_score = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == home_team_id)
        away_score = sum(safe_int(p.get("tot_score"), 0) for p in player_stats if p.get("team_id") == away_team_id)

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
        {"label": "Field Goals", "home": f"{home_fgm}/{home_fga}", "away": f"{away_fgm}/{away_fga}"},
        {"label": "3-Pointers", "home": f"{home_3pm}/{home_3pa}", "away": f"{away_3pm}/{away_3pa}"},
        {"label": "Free Throws", "home": f"{home_ftm}/{home_fta}", "away": f"{away_ftm}/{away_fta}"},
        {"label": "Rebounds", "home": f"{home_oreb + home_dreb}", "away": f"{away_oreb + away_dreb}"},
        {"label": "Assists", "home": home_ast, "away": away_ast},
        {"label": "Turnovers", "home": home_tov, "away": away_tov},
        {"label": "Steals", "home": home_stl, "away": away_stl},
        {"label": "Blocks", "home": home_blk, "away": away_blk},
        {"label": "Fouls", "home": home_pf, "away": away_pf},
    ]

    # Return GameData format
    result = {
        "league": league,
        "date": formatted_date,
        "status": status,
        "homeTeam": {
            "name": home_team_name,
            "shortName": home_team_name,  # Can be abbreviated later
            "logo": "",  # Empty string shows placeholder
            "record": "",  # No record data available
            "score": home_score,
            "players": home_players
        },
        "awayTeam": {
            "name": away_team_name,
            "shortName": away_team_name,
            "logo": "",
            "record": "",
            "score": away_score,
            "players": away_players
        },
        "gameRecords": game_records
    }

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[get_game_details_handler] Returning data: {result}")

    return result
