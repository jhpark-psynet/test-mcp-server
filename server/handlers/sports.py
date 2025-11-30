"""스포츠 데이터 핸들러."""
from typing import Any, Dict, List

from server.services.sports import SportsClientFactory
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

            if state == "f":  # Finished
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

    # Get game info - try MOCK DB first, then search recent dates in real API
    game_info = None

    # Try MOCK DB first
    for games in MOCK_GAMES_DB.values():
        for game in games:
            if game["game_id"] == game_id:
                game_info = game
                break
        if game_info:
            break

    # If not found in MOCK, search recent dates in real API
    if not game_info:
        from datetime import datetime, timedelta
        today = datetime.now()

        # Search last 7 days
        for days_ago in range(7):
            search_date = (today - timedelta(days=days_ago)).strftime("%Y%m%d")
            try:
                games = client.get_games_by_sport(search_date)
                for game in games:
                    if game.get("game_id") == game_id:
                        game_info = game
                        break
                if game_info:
                    break
            except:
                continue

    if not game_info:
        raise ValueError(f"Game {game_id} not found")

    # Check if game is finished (state: F for finished, B for before, etc.)
    state = game_info.get("state", "").upper()
    if state != "F":
        raise ValueError(f"Game {game_id} has not finished yet (state: {state}). Stats not available.")

    # Get team stats
    team_stats = client.get_team_stats(game_id)
    if not team_stats or len(team_stats) < 2:
        raise ValueError(f"Team stats not found for game {game_id}")

    # Get player stats
    player_stats = client.get_player_stats(game_id)
    if not player_stats:
        raise ValueError(f"Player stats not found for game {game_id}")

    # Format date: "20251118" -> "11.18 (월)"
    match_date = game_info.get("match_date", "")
    formatted_date = f"{match_date[4:6]}.{match_date[6:8]}"

    # Map state to status (handle both uppercase and lowercase)
    state_raw = game_info.get("state", "").upper()
    state_map = {"F": "종료", "진행중": "진행중", "B": "예정"}
    status = state_map.get(state_raw, "예정")

    # League name
    league = game_info.get("league_name", "NBA")

    # Home team info
    home_team_name = game_info.get("home_team_name", "")
    home_score = int(game_info.get("home_score", 0))

    # Away team info
    away_team_name = game_info.get("away_team_name", "")
    away_score = int(game_info.get("away_score", 0))

    # Extract team IDs
    home_team_id = game_info.get("home_team_id", "")
    away_team_id = game_info.get("away_team_id", "")

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
            "number": int(player.get("back_no", 0)),
            "name": player.get("player_name", "Unknown"),
            "position": player.get("pos_sc", "-"),
            "minutes": minutes,
            "rebounds": int(player.get("treb_cn", 0)),
            "assists": int(player.get("assist_cn", 0)),
            "points": int(player.get("tot_score", 0))
        }

        if player_team_id == home_team_id:
            home_players.append(player_data)
        elif player_team_id == away_team_id:
            away_players.append(player_data)

    # Build game records from team stats
    home_stats = team_stats[0]
    away_stats = team_stats[1]

    home_fgm = int(home_stats.get("home_team_fgm_cn", 0))
    home_fga = int(home_stats.get("home_team_fga_cn", 1))
    away_fgm = int(away_stats.get("away_team_fgm_cn", 0))
    away_fga = int(away_stats.get("away_team_fga_cn", 1))

    home_3pm = int(home_stats.get("home_team_pgm3_cn", 0))
    home_3pa = int(home_stats.get("home_team_pga3_cn", 1))
    away_3pm = int(away_stats.get("away_team_pgm3_cn", 0))
    away_3pa = int(away_stats.get("away_team_pga3_cn", 1))

    home_ftm = int(home_stats.get("home_team_ftm_cn", 0))
    home_fta = int(home_stats.get("home_team_fta_cn", 1))
    away_ftm = int(away_stats.get("away_team_ftm_cn", 0))
    away_fta = int(away_stats.get("away_team_fta_cn", 1))

    home_oreb = int(home_stats.get("home_team_oreb_cn", 0))
    home_dreb = int(home_stats.get("home_team_dreb_cn", 0))
    away_oreb = int(away_stats.get("away_team_oreb_cn", 0))
    away_dreb = int(away_stats.get("away_team_dreb_cn", 0))

    home_ast = int(home_stats.get("home_team_assist_cn", 0))
    away_ast = int(away_stats.get("away_team_assist_cn", 0))

    home_tov = int(home_stats.get("home_team_turnover_cn", 0))
    away_tov = int(away_stats.get("away_team_turnover_cn", 0))

    home_stl = int(home_stats.get("home_team_steal_cn", 0))
    away_stl = int(away_stats.get("away_team_steal_cn", 0))

    home_blk = int(home_stats.get("home_team_block_cn", 0))
    away_blk = int(away_stats.get("away_team_block_cn", 0))

    home_pf = int(home_stats.get("home_team_pfoul_cn", 0))
    away_pf = int(away_stats.get("away_team_pfoul_cn", 0))

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
