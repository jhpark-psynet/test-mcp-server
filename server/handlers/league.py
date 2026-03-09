"""리그 목록 핸들러."""
import logging
from typing import Any, Dict

from server.handlers.game_list import SPORT_CODE_MAP, SPORT_NAME_MAP

logger = logging.getLogger(__name__)


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
