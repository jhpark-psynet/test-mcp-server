"""스포츠 데이터 API 클라이언트 (Mock + Real API)."""
from typing import Dict, List, Any, Optional
import logging
import httpx

from server.config import CONFIG
from server.services.api_response_mapper import ApiResponseMapper
from server.services.mock_sports_data import (
    MOCK_GAMES_DB,
    MOCK_TEAM_STATS_DB,
    MOCK_PLAYER_STATS_DB
)

logger = logging.getLogger(__name__)


class SportsApiClient:
    """스포츠 데이터 API 클라이언트 (Mock + Real API).

    USE_MOCK_SPORTS_DATA 설정에 따라 Mock 데이터 또는 실제 API를 사용합니다.
    """

    def __init__(self):
        """Initialize sports API client."""
        self.use_mock = CONFIG.use_mock_sports_data
        self.base_url = CONFIG.sports_api_base_url
        self.api_key = CONFIG.sports_api_key
        self.timeout = CONFIG.sports_api_timeout_s

        if self.use_mock:
            logger.info("SportsApiClient initialized with MOCK data")
        elif CONFIG.has_sports_api:
            logger.info(f"SportsApiClient initialized with REAL API: {self.base_url}")
        else:
            logger.warning("SportsApiClient: Real API requested but not configured. Falling back to mock data.")
            self.use_mock = True

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """실제 API에 HTTP 요청을 보냅니다.

        Args:
            endpoint: API 엔드포인트 경로 (예: "/games")
            params: 요청 파라미터

        Returns:
            API 응답 (JSON)

        Raises:
            httpx.HTTPStatusError: HTTP 에러 발생 시
            httpx.TimeoutException: 타임아웃 발생 시
            Exception: 기타 에러
        """
        # API Key를 파라미터에 추가
        params_with_key = {**params, "auth_key": self.api_key}

        # 전체 URL 구성
        # TODO: API_INTEGRATION.md 작성 후 실제 endpoint 경로로 업데이트
        # 예: url = f"{self.base_url}{endpoint}"
        # 현재는 base_url이 전체 경로인 경우를 가정
        url = self.base_url if not endpoint else f"{self.base_url}{endpoint}"

        logger.debug(f"Making request to {url} with params: {params}")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params_with_key)
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {url}")
            raise ValueError(f"API request timed out after {self.timeout}s") from e

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 404:
                raise ValueError(f"API endpoint not found: {url}") from e
            elif e.response.status_code >= 500:
                raise ValueError(f"API server error: {e.response.status_code}") from e
            else:
                raise ValueError(f"API request failed: {e.response.status_code}") from e

        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}")
            raise ValueError(f"API request failed: {str(e)}") from e

    def get_games_by_sport(self, date: str, sport: str) -> List[Dict[str, Any]]:
        """특정 날짜의 스포츠 경기 목록 조회.

        Args:
            date: 조회 날짜 (YYYYMMDD)
            sport: 스포츠 종목 (basketball, baseball, football)

        Returns:
            경기 목록

        Raises:
            ValueError: 잘못된 날짜 형식 또는 스포츠 종목
        """
        if sport not in ["basketball", "baseball", "football"]:
            raise ValueError(f"Invalid sport: {sport}. Must be one of: basketball, baseball, football")

        if len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid date format: {date}. Must be YYYYMMDD")

        # Mock 데이터 사용
        if self.use_mock:
            key = f"{date}_{sport}"
            games = MOCK_GAMES_DB.get(key, [])
            logger.info(f"[MOCK] Retrieved {len(games)} games for {sport} on {date}")
            return games

        # 실제 API 호출
        params = {
            "date": date,
            "sport": sport,
        }

        try:
            response = self._make_request("/data3V1/livescore/gameList", params)
            games = ApiResponseMapper.map_games_list(response)
            logger.info(f"[REAL API] Retrieved {len(games)} games for {sport} on {date}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch games from API: {e}")
            raise

    def get_team_stats(self, game_id: str, sport: str) -> Optional[List[Dict[str, Any]]]:
        """경기의 팀별 기록 조회.

        Args:
            game_id: 경기 ID
            sport: 스포츠 종목 (basketball, soccer, volleyball)

        Returns:
            팀 기록 배열 [home_team, away_team] 또는 None

        Raises:
            ValueError: 경기를 찾을 수 없거나 아직 시작하지 않은 경기
        """
        # Mock 데이터 사용
        if self.use_mock:
            stats = MOCK_TEAM_STATS_DB.get(game_id)

            if stats is None:
                # Check if game exists but hasn't started
                for games in MOCK_GAMES_DB.values():
                    for game in games:
                        if game["game_id"] == game_id:
                            if game["state"] == "b":
                                raise ValueError(f"Game {game_id} has not started yet. Team stats not available.")
                            break

                raise ValueError(f"Game {game_id} not found")

            logger.info(f"[MOCK] Retrieved team stats for game {game_id}")
            return stats

        # 실제 API 호출 - 스포츠별 endpoint 선택
        if sport == "basketball":
            endpoint = "/data3V1/livescore/basketballTeamStat"
        elif sport == "soccer":
            endpoint = "/data3V1/livescore/soccerTeamStat"
        elif sport == "volleyball":
            endpoint = "/data3V1/livescore/volleyballTeamStat"
        else:
            raise ValueError(f"Unsupported sport: {sport}")

        params = {
            "game_id": game_id,
        }

        try:
            response = self._make_request(endpoint, params)
            stats = ApiResponseMapper.map_team_stats_list(response, sport)

            if not stats:
                raise ValueError(f"No team stats found for game {game_id}")

            logger.info(f"[REAL API] Retrieved {sport} team stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch team stats from API: {e}")
            raise

    def get_player_stats(self, game_id: str, sport: str) -> Optional[List[Dict[str, Any]]]:
        """경기의 선수별 기록 조회.

        Args:
            game_id: 경기 ID
            sport: 스포츠 종목 (basketball, soccer, volleyball)

        Returns:
            선수 기록 배열 또는 None

        Raises:
            ValueError: 경기를 찾을 수 없거나 아직 시작하지 않은 경기
        """
        # Mock 데이터 사용
        if self.use_mock:
            stats = MOCK_PLAYER_STATS_DB.get(game_id)

            if stats is None:
                # Check if game exists but hasn't started
                for games in MOCK_GAMES_DB.values():
                    for game in games:
                        if game["game_id"] == game_id:
                            if game["state"] == "b":
                                raise ValueError(f"Game {game_id} has not started yet. Player stats not available.")
                            break

                raise ValueError(f"Game {game_id} not found")

            logger.info(f"[MOCK] Retrieved player stats for game {game_id}")
            return stats

        # 실제 API 호출 - 스포츠별 endpoint 선택
        if sport == "basketball":
            endpoint = "/data3V1/livescore/basketballPlayerStat"
        elif sport == "soccer":
            endpoint = "/data3V1/livescore/soccerPlayerStat"
        elif sport == "volleyball":
            endpoint = "/data3V1/livescore/volleyballPlayerStat"
        else:
            raise ValueError(f"Unsupported sport: {sport}")

        params = {
            "game_id": game_id,
        }

        try:
            response = self._make_request(endpoint, params)
            stats = ApiResponseMapper.map_player_stats_list(response, sport)

            if not stats:
                raise ValueError(f"No player stats found for game {game_id}")

            logger.info(f"[REAL API] Retrieved {sport} player stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch player stats from API: {e}")
            raise
