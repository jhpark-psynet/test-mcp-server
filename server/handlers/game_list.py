"""경기 목록 핸들러."""
import logging
from typing import Any, Dict, List

from server.services.sports import SportsClientFactory
from server.services.cache import (
  cache_games,
  get_cached_games,
  invalidate_cache,
)

logger = logging.getLogger(__name__)

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
