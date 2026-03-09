"""게임 상세 핸들러 진입점."""
import logging
from typing import Any, Dict

from server.services.sports import SportsClientFactory
from server.handlers._game_details_shared import (
  _get_game_info,
  _extract_basic_info,
  _build_scheduled_game_response,
  _build_live_or_finished_game_response,
)

logger = logging.getLogger(__name__)


async def get_game_details_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
  """경기의 상세 정보를 조회하는 핸들러 (위젯용).

  모든 스포츠에 대응하는 범용 핸들러.
  스포츠별 특화 로직은 client와 mapper에 위임.
  """
  game_id = arguments.get("game_id", "").strip()
  sport = arguments.get("sport", "basketball").strip()
  date_param = arguments.get("date", "").strip()

  try:
    # For baseball, use a completely different flow (single total_info API call)
    if sport == "baseball":
      from server.services.sports.baseball import BaseballClient
      from server.handlers.baseball import build_baseball_game_response
      client: BaseballClient = SportsClientFactory.create_client("baseball")
      return await build_baseball_game_response(client, game_id)

    # For basketball (real API), use single basketballGameTotalInfo API call
    if sport == "basketball":
      from server.services.sports.basketball import BasketballClient
      from server.handlers.basketball import build_basketball_game_response
      bball_client: BasketballClient = SportsClientFactory.create_client("basketball")
      if not bball_client.use_mock:
        return await build_basketball_game_response(bball_client, game_id)
      # Mock mode: fall through to old multi-API flow using existing bball_client
      client = bball_client
    else:
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

  except ValueError as exc:
    logger.warning(f"[get_game_details] Data not found for {game_id} ({sport}): {exc}")
    from server.errors import APIError, APIErrorCode
    raise APIError(APIErrorCode.DATA_NOT_FOUND, detail=str(exc))
