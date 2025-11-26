"""스포츠 데이터 핸들러."""
import json
from typing import Any, Dict, List

from server.services.sports_api_client import SportsApiClient
from server.services.mock_sports_data import MOCK_GAMES_DB


# Global sports API client instance
_sports_client = SportsApiClient()


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
    games = _sports_client.get_games_by_sport(date, sport)

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


def get_team_stats_handler(arguments: Dict[str, Any]) -> str:
    """경기의 팀별 기록을 조회하는 핸들러.

    Args:
        arguments: Tool arguments with 'game_id' and 'sport' fields

    Returns:
        Formatted team stats

    Raises:
        ValueError: Game not found or game not finished
        Exception: Other errors during processing
    """
    game_id = arguments.get("game_id", "")
    sport = arguments.get("sport", "basketball")

    # Let exceptions bubble up so server_factory can set isError=True
    stats = _sports_client.get_team_stats(game_id, sport)

    if not stats or len(stats) < 2:
        raise ValueError(f"No team stats found for game {game_id}")

    # Extract from array structure: [home_team, away_team]
    home_team = stats[0]
    away_team = stats[1]

    home_name = home_team.get("home_team_name", "Home Team")
    away_name = away_team.get("away_team_name", "Away Team")

    # Convert string values to integers
    home_fgm = int(home_team.get("home_team_fgm_cn", 0))
    home_fga = int(home_team.get("home_team_fga_cn", 1))
    away_fgm = int(away_team.get("away_team_fgm_cn", 0))
    away_fga = int(away_team.get("away_team_fga_cn", 1))

    home_3pm = int(home_team.get("home_team_pgm3_cn", 0))
    home_3pa = int(home_team.get("home_team_pga3_cn", 1))
    away_3pm = int(away_team.get("away_team_pgm3_cn", 0))
    away_3pa = int(away_team.get("away_team_pga3_cn", 1))

    home_ftm = int(home_team.get("home_team_ftm_cn", 0))
    home_fta = int(home_team.get("home_team_fta_cn", 1))
    away_ftm = int(away_team.get("away_team_ftm_cn", 0))
    away_fta = int(away_team.get("away_team_fta_cn", 1))

    home_oreb = int(home_team.get("home_team_oreb_cn", 0))
    home_dreb = int(home_team.get("home_team_dreb_cn", 0))
    away_oreb = int(away_team.get("away_team_oreb_cn", 0))
    away_dreb = int(away_team.get("away_team_dreb_cn", 0))

    home_ast = int(home_team.get("home_team_assist_cn", 0))
    away_ast = int(away_team.get("away_team_assist_cn", 0))

    home_tov = int(home_team.get("home_team_turnover_cn", 0))
    away_tov = int(away_team.get("away_team_turnover_cn", 0))

    home_stl = int(home_team.get("home_team_steal_cn", 0))
    away_stl = int(away_team.get("away_team_steal_cn", 0))

    home_blk = int(home_team.get("home_team_block_cn", 0))
    away_blk = int(away_team.get("away_team_block_cn", 0))

    home_pf = int(home_team.get("home_team_pfoul_cn", 0))
    away_pf = int(away_team.get("away_team_pfoul_cn", 0))

    # Calculate percentages
    home_fg_pct = (home_fgm / home_fga) * 100 if home_fga > 0 else 0
    away_fg_pct = (away_fgm / away_fga) * 100 if away_fga > 0 else 0
    home_3p_pct = (home_3pm / home_3pa) * 100 if home_3pa > 0 else 0
    away_3p_pct = (away_3pm / away_3pa) * 100 if away_3pa > 0 else 0
    home_ft_pct = (home_ftm / home_fta) * 100 if home_fta > 0 else 0
    away_ft_pct = (away_ftm / away_fta) * 100 if away_fta > 0 else 0

    # Build formatted response
    lines = [
        f"## Team Statistics - Game {game_id}\n",
        f"### {home_name} vs {away_name}\n",
        "| Stat | Home | Away |",
        "|------|------|------|",
        f"| **Team** | {home_name} | {away_name} |",
        f"| Field Goals | {home_fgm}/{home_fga} ({home_fg_pct:.1f}%) | {away_fgm}/{away_fga} ({away_fg_pct:.1f}%) |",
        f"| 3-Pointers | {home_3pm}/{home_3pa} ({home_3p_pct:.1f}%) | {away_3pm}/{away_3pa} ({away_3p_pct:.1f}%) |",
        f"| Free Throws | {home_ftm}/{home_fta} ({home_ft_pct:.1f}%) | {away_ftm}/{away_fta} ({away_ft_pct:.1f}%) |",
        f"| Rebounds | {home_oreb + home_dreb} ({home_oreb}+{home_dreb}) | {away_oreb + away_dreb} ({away_oreb}+{away_dreb}) |",
        f"| Assists | {home_ast} | {away_ast} |",
        f"| Turnovers | {home_tov} | {away_tov} |",
        f"| Steals | {home_stl} | {away_stl} |",
        f"| Blocks | {home_blk} | {away_blk} |",
        f"| Fouls | {home_pf} | {away_pf} |",
    ]

    return "\n".join(lines)


def get_player_stats_handler(arguments: Dict[str, Any]) -> str:
    """경기의 선수별 기록을 조회하는 핸들러.

    Args:
        arguments: Tool arguments with 'game_id' and 'sport' fields

    Returns:
        Formatted player stats

    Raises:
        ValueError: Game not found or game not finished
        Exception: Other errors during processing
    """
    game_id = arguments.get("game_id", "")
    sport = arguments.get("sport", "basketball")

    # Let exceptions bubble up so server_factory can set isError=True
    stats = _sports_client.get_player_stats(game_id, sport)

    if not stats:
        raise ValueError(f"No player stats found for game {game_id}")

    # Group players by team_id
    teams: Dict[str, list] = {}
    for player in stats:
        team_id = player.get("team_id", "")
        if team_id not in teams:
            teams[team_id] = []
        teams[team_id].append(player)

    # Get team IDs
    team_ids = list(teams.keys())
    if len(team_ids) < 2:
        raise ValueError(f"Expected 2 teams but found {len(team_ids)}")

    # Get team names from team stats
    try:
        team_stats = _sports_client.get_team_stats(game_id, sport)
        home_name = team_stats[0].get("home_team_name", f"Team {team_ids[0]}")
        away_name = team_stats[1].get("away_team_name", f"Team {team_ids[1]}")
        home_team_id = team_stats[0].get("home_team_id", team_ids[0])
        away_team_id = team_stats[1].get("away_team_id", team_ids[1])
    except Exception:
        # Fallback if team stats not available
        home_team_id = team_ids[0]
        away_team_id = team_ids[1]
        home_name = f"Team {home_team_id}"
        away_name = f"Team {away_team_id}"

    home_players = teams.get(home_team_id, [])
    away_players = teams.get(away_team_id, [])

    # Build formatted response
    lines = [
        f"## Player Statistics - Game {game_id}\n",
    ]

    # Home team players
    lines.append(f"### {home_name}\n")
    lines.append("| Player | Pos | Time | PTS | REB | AST | STL | BLK | FG | 3PT | FG% | Season Avg (PTS/REB/AST) |")
    lines.append("|--------|-----|------|-----|-----|-----|-----|-----|-------|---------|-----|--------------------------|")

    for player in home_players:
        name = player.get("player_name", "Unknown")
        pos = player.get("pos_sc", "-")
        time = player.get("player_time", "0:00:00")[:5]  # HH:MM
        pts = player.get("tot_score", 0)
        reb = player.get("treb_cn", 0)
        ast = player.get("assist_cn", 0)
        stl = player.get("steal_cn", 0)
        blk = player.get("blocks", 0)
        fgm = player.get("fgm_cn", 0)
        fga = player.get("fga_cn", 0)
        pgm3 = player.get("pgm3_cn", 0)
        fg_pct = player.get("fgpct", "0")
        s_pts = player.get("s_pts_avg", 0)
        s_reb = player.get("s_tr_avg", 0)
        s_ast = player.get("s_ass_avg", 0)

        lines.append(
            f"| {name} | {pos} | {time} | {pts} | {reb} | {ast} | {stl} | {blk} | "
            f"{fgm}/{fga} | {pgm3} | {fg_pct} | {s_pts}/{s_reb}/{s_ast} |"
        )

    lines.append("")

    # Away team players
    lines.append(f"### {away_name}\n")
    lines.append("| Player | Pos | Time | PTS | REB | AST | STL | BLK | FG | 3PT | FG% | Season Avg (PTS/REB/AST) |")
    lines.append("|--------|-----|------|-----|-----|-----|-----|-----|-------|---------|-----|--------------------------|")

    for player in away_players:
        name = player.get("player_name", "Unknown")
        pos = player.get("pos_sc", "-")
        time = player.get("player_time", "0:00:00")[:5]  # HH:MM
        pts = player.get("tot_score", 0)
        reb = player.get("treb_cn", 0)
        ast = player.get("assist_cn", 0)
        stl = player.get("steal_cn", 0)
        blk = player.get("blocks", 0)
        fgm = player.get("fgm_cn", 0)
        fga = player.get("fga_cn", 0)
        pgm3 = player.get("pgm3_cn", 0)
        fg_pct = player.get("fgpct", "0")
        s_pts = player.get("s_pts_avg", 0)
        s_reb = player.get("s_tr_avg", 0)
        s_ast = player.get("s_ass_avg", 0)

        lines.append(
            f"| {name} | {pos} | {time} | {pts} | {reb} | {ast} | {stl} | {blk} | "
            f"{fgm}/{fga} | {pgm3} | {fg_pct} | {s_pts}/{s_reb}/{s_ast} |"
        )

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

    # Get game info
    game_info = None
    for games in MOCK_GAMES_DB.values():
        for game in games:
            if game["game_id"] == game_id:
                game_info = game
                break
        if game_info:
            break

    if not game_info:
        raise ValueError(f"Game {game_id} not found")

    if game_info.get("state") != "f":
        raise ValueError(f"Game {game_id} has not finished yet. Stats not available.")

    # Get team stats
    team_stats = _sports_client.get_team_stats(game_id, sport)
    if not team_stats or len(team_stats) < 2:
        raise ValueError(f"Team stats not found for game {game_id}")

    # Get player stats
    player_stats = _sports_client.get_player_stats(game_id, sport)
    if not player_stats:
        raise ValueError(f"Player stats not found for game {game_id}")

    # Format date: "20251118" -> "11.18 (월)"
    match_date = game_info.get("match_date", "")
    formatted_date = f"{match_date[4:6]}.{match_date[6:8]}"

    # Map state to status
    state_map = {"f": "종료", "진행중": "진행중", "b": "예정"}
    status = state_map.get(game_info.get("state", ""), "예정")

    # League name
    league = game_info.get("league_name", "NBA")

    # Home team info
    home_team_name = game_info.get("home_team_name", "")
    home_score = game_info.get("home_score", 0)

    # Away team info
    away_team_name = game_info.get("away_team_name", "")
    away_score = game_info.get("away_score", 0)

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
