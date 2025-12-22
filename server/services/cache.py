"""TTL 기반 인메모리 캐시.

게임 목록을 날짜+스포츠 키로 캐싱하여 중복 API 호출을 방지합니다.
불완전한 데이터는 캐시하지 않습니다.
"""
from typing import Any, Dict, List, Optional

from cachetools import TTLCache
import logging

from server.config import CONFIG

logger = logging.getLogger(__name__)

# 캐시 인스턴스 (CONFIG에서 설정값 로드)
_game_list_cache: TTLCache = TTLCache(
    maxsize=CONFIG.cache_max_size,
    ttl=CONFIG.cache_ttl_seconds,
)

# 게임 데이터 필수 필드 (이 필드가 없으면 캐시하지 않음)
REQUIRED_GAME_FIELDS = {"game_id", "home_team_name", "away_team_name"}


def _make_key(date: str, sport: str) -> str:
    """캐시 키 생성.

    Args:
        date: 날짜 (YYYYMMDD 형식)
        sport: 스포츠 종류 (basketball, soccer 등)

    Returns:
        캐시 키 문자열 (예: "20241222_basketball")
    """
    return f"{date}_{sport}"


def _is_valid_game(game: Dict[str, Any]) -> bool:
    """게임 데이터가 캐시할 만큼 유효한지 검증.

    Args:
        game: 게임 데이터 딕셔너리

    Returns:
        필수 필드가 모두 존재하고 비어있지 않으면 True
    """
    for field in REQUIRED_GAME_FIELDS:
        value = game.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            return False
    return True


def _validate_games(games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """게임 목록에서 유효한 게임만 필터링.

    Args:
        games: 게임 목록

    Returns:
        유효한 게임만 포함된 목록
    """
    valid_games = [g for g in games if _is_valid_game(g)]

    if len(valid_games) < len(games):
        invalid_count = len(games) - len(valid_games)
        logger.warning(
            f"Filtered {invalid_count} invalid games (missing required fields: {REQUIRED_GAME_FIELDS})"
        )

    return valid_games


def cache_games(date: str, sport: str, games: List[Dict[str, Any]]) -> bool:
    """게임 목록을 검증 후 캐시에 저장.

    Args:
        date: 날짜 (YYYYMMDD)
        sport: 스포츠 종류
        games: 게임 목록 (API 응답 데이터)

    Returns:
        캐시 저장 성공 여부 (유효한 게임이 1개 이상이면 True)
    """
    if not games:
        logger.debug(f"Cache skip: empty games list for {date}_{sport}")
        return False

    # 유효한 게임만 필터링
    valid_games = _validate_games(games)

    if not valid_games:
        logger.warning(f"Cache skip: no valid games for {date}_{sport}")
        return False

    key = _make_key(date, sport)
    _game_list_cache[key] = valid_games
    logger.debug(f"Cache store: key={key}, count={len(valid_games)}")
    return True


def get_cached_games(date: str, sport: str) -> Optional[List[Dict[str, Any]]]:
    """캐시에서 게임 목록 조회.

    Args:
        date: 날짜 (YYYYMMDD)
        sport: 스포츠 종류

    Returns:
        캐시된 게임 목록 또는 None (캐시 미스)
    """
    key = _make_key(date, sport)
    games = _game_list_cache.get(key)

    if games is not None:
        logger.debug(f"Cache hit: key={key}, count={len(games)}")
    else:
        logger.debug(f"Cache miss: key={key}")

    return games


def invalidate_cache(date: str, sport: str) -> bool:
    """특정 키의 캐시를 무효화.

    force_refresh 시 기존 캐시를 삭제하는 데 사용.

    Args:
        date: 날짜 (YYYYMMDD)
        sport: 스포츠 종류

    Returns:
        삭제 성공 여부 (키가 존재했으면 True)
    """
    key = _make_key(date, sport)
    if key in _game_list_cache:
        del _game_list_cache[key]
        logger.debug(f"Cache invalidated: key={key}")
        return True
    return False


def find_game_in_cache(
    date: str,
    sport: str,
    game_id: str,
) -> Optional[Dict[str, Any]]:
    """캐시에서 특정 게임 조회.

    Args:
        date: 날짜 (YYYYMMDD)
        sport: 스포츠 종류
        game_id: 게임 ID

    Returns:
        게임 정보 딕셔너리 또는 None
    """
    games = get_cached_games(date, sport)
    if games:
        for game in games:
            if game.get("game_id") == game_id:
                logger.debug(f"Cache find: game_id={game_id} found")
                return game
    return None


def clear_cache() -> None:
    """캐시 전체 삭제 (테스트용).

    테스트 격리를 위해 사용합니다.
    """
    _game_list_cache.clear()
    logger.debug("Cache cleared")


def get_cache_info() -> Dict[str, Any]:
    """캐시 상태 정보 반환 (디버깅용).

    Returns:
        캐시 크기, 최대 크기, TTL 정보
    """
    return {
        "current_size": len(_game_list_cache),
        "max_size": _game_list_cache.maxsize,
        "ttl": _game_list_cache.ttl,
    }
