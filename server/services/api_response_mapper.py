"""API 응답 데이터를 내부 포맷으로 변환하는 매퍼."""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ApiResponseMapper:
    """실제 Sports API 응답을 내부 데이터 구조로 변환합니다.

    이 클래스는 실제 API 응답 필드명을 Mock 데이터와 동일한 구조로 변환합니다.
    API_INTEGRATION.md의 필드 매핑 정보를 기반으로 구현됩니다.
    """

    # 필드 매핑 테이블 (API_INTEGRATION.md 작성 후 채워야 함)
    # TODO: API_INTEGRATION.md 문서를 작성한 후 실제 API 필드명으로 업데이트하세요

    # 경기 목록 필드 매핑 (API 대문자 -> 내부 소문자)
    GAME_FIELD_MAP = {
        "GAME_ID": "game_id",
        "LEAGUE_NAME": "league_name",
        "MATCH_DATE": "match_date",
        "MATCH_TIME": "match_time",
        "HOME_TEAM_ID": "home_team_id",
        "AWAY_TEAM_ID": "away_team_id",
        "HOME_TEAM_NAME": "home_team_name",
        "AWAY_TEAM_NAME": "away_team_name",
        "HOME_SCORE": "home_score",
        "AWAY_SCORE": "away_score",
        "STATE": "state",
        "ARENA_NAME": "arena_name",
        "COMPE": "compe",
    }

    # 농구 팀 통계 필드 매핑
    BASKETBALL_TEAM_STATS_FIELD_MAP = {
        # TODO: basketballTeamStat endpoint 응답 확인 후 추가
    }

    # 농구 선수 통계 필드 매핑
    BASKETBALL_PLAYER_STATS_FIELD_MAP = {
        # TODO: basketballPlayerStat endpoint 응답 확인 후 추가
    }

    # 축구 팀 통계 필드 매핑
    SOCCER_TEAM_STATS_FIELD_MAP = {
        # TODO: soccerTeamStat endpoint 응답 확인 후 추가
    }

    # 축구 선수 통계 필드 매핑
    SOCCER_PLAYER_STATS_FIELD_MAP = {
        # TODO: soccerPlayerStat endpoint 응답 확인 후 추가
    }

    # 배구 팀 통계 필드 매핑
    VOLLEYBALL_TEAM_STATS_FIELD_MAP = {
        # TODO: volleyballTeamStat endpoint 응답 확인 후 추가
    }

    # 배구 선수 통계 필드 매핑
    VOLLEYBALL_PLAYER_STATS_FIELD_MAP = {
        # TODO: volleyballPlayerStat endpoint 응답 확인 후 추가
    }

    @staticmethod
    def map_game(api_game: Dict[str, Any]) -> Dict[str, Any]:
        """경기 데이터를 내부 포맷으로 변환.

        Args:
            api_game: 실제 API에서 반환된 경기 데이터

        Returns:
            내부 포맷으로 변환된 경기 데이터
        """
        # 매핑 테이블이 비어있으면 그대로 반환 (API가 이미 올바른 포맷인 경우)
        if not ApiResponseMapper.GAME_FIELD_MAP:
            logger.debug("GAME_FIELD_MAP is empty, returning API response as-is")
            return api_game

        # 필드 매핑 적용
        mapped = {}
        for api_field, internal_field in ApiResponseMapper.GAME_FIELD_MAP.items():
            if api_field in api_game:
                mapped[internal_field] = api_game[api_field]
            else:
                logger.warning(f"Field '{api_field}' not found in API response")

        # 매핑되지 않은 필드도 유지 (추가 데이터)
        for key, value in api_game.items():
            if key not in ApiResponseMapper.GAME_FIELD_MAP and key not in mapped:
                mapped[key] = value

        return mapped

    @staticmethod
    def map_games_list(api_response: Any) -> List[Dict[str, Any]]:
        """경기 목록 API 응답을 내부 포맷으로 변환.

        Args:
            api_response: 실제 API 응답 (전체 response)

        Returns:
            경기 목록 (내부 포맷)
        """
        # API 응답이 직접 리스트인 경우
        if isinstance(api_response, list):
            return [ApiResponseMapper.map_game(game) for game in api_response]

        # API 응답이 dict이고 특정 키에 리스트가 있는 경우
        if isinstance(api_response, dict):
            # 실제 API 구조: {"Data": {"list": [...]}}
            if "Data" in api_response and isinstance(api_response["Data"], dict):
                games_list = api_response["Data"].get("list", [])
                if isinstance(games_list, list):
                    logger.debug(f"Found {len(games_list)} games in 'Data.list'")
                    return [ApiResponseMapper.map_game(game) for game in games_list]

            # 일반적인 응답 구조 시도
            for key in ["games", "data", "results", "items", "list"]:
                if key in api_response and isinstance(api_response[key], list):
                    logger.debug(f"Found games list in '{key}' field")
                    return [ApiResponseMapper.map_game(game) for game in api_response[key]]

            logger.warning("Could not find games list in API response")
            return []

        logger.error(f"Unexpected API response type: {type(api_response)}")
        return []

    @staticmethod
    def map_team_stats(api_stats: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """팀 통계 데이터를 내부 포맷으로 변환.

        Args:
            api_stats: 실제 API에서 반환된 팀 통계 데이터
            sport: 스포츠 종목 (basketball, soccer, volleyball)

        Returns:
            내부 포맷으로 변환된 팀 통계 데이터
        """
        # 스포츠별 필드 매핑 선택
        if sport == "basketball":
            field_map = ApiResponseMapper.BASKETBALL_TEAM_STATS_FIELD_MAP
        elif sport == "soccer":
            field_map = ApiResponseMapper.SOCCER_TEAM_STATS_FIELD_MAP
        elif sport == "volleyball":
            field_map = ApiResponseMapper.VOLLEYBALL_TEAM_STATS_FIELD_MAP
        else:
            logger.warning(f"Unknown sport: {sport}, returning as-is")
            return api_stats

        # 매핑이 비어있으면 그대로 반환
        if not field_map:
            logger.debug(f"Field map for {sport} team stats is empty, returning as-is")
            return api_stats

        mapped = {}
        for api_field, internal_field in field_map.items():
            if api_field in api_stats:
                mapped[internal_field] = api_stats[api_field]

        # 매핑되지 않은 필드도 유지
        for key, value in api_stats.items():
            if key not in field_map and key not in mapped:
                mapped[key] = value

        return mapped

    @staticmethod
    def map_team_stats_list(api_response: Any, sport: str) -> List[Dict[str, Any]]:
        """팀 통계 목록 API 응답을 내부 포맷으로 변환.

        Args:
            api_response: 실제 API 응답
            sport: 스포츠 종목 (basketball, soccer, volleyball)

        Returns:
            팀 통계 목록 [home_team, away_team]
        """
        if isinstance(api_response, list):
            return [ApiResponseMapper.map_team_stats(stats, sport) for stats in api_response]

        if isinstance(api_response, dict):
            # 실제 API 구조: {"Data": {"list": [...]}} 또는 {"Data": [...]}
            if "Data" in api_response:
                data = api_response["Data"]
                if isinstance(data, dict) and "list" in data:
                    stats_list = data["list"]
                    if isinstance(stats_list, list):
                        return [ApiResponseMapper.map_team_stats(stats, sport) for stats in stats_list]
                elif isinstance(data, list):
                    return [ApiResponseMapper.map_team_stats(stats, sport) for stats in data]

            # 일반적인 응답 구조 시도
            for key in ["team_stats", "teams", "data", "list"]:
                if key in api_response and isinstance(api_response[key], list):
                    return [ApiResponseMapper.map_team_stats(stats, sport) for stats in api_response[key]]

            logger.warning("Could not find team stats list in API response")
            return []

        return []

    @staticmethod
    def map_player_stats(api_stats: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """선수 통계 데이터를 내부 포맷으로 변환.

        Args:
            api_stats: 실제 API에서 반환된 선수 통계 데이터
            sport: 스포츠 종목 (basketball, soccer, volleyball)

        Returns:
            내부 포맷으로 변환된 선수 통계 데이터
        """
        # 스포츠별 필드 매핑 선택
        if sport == "basketball":
            field_map = ApiResponseMapper.BASKETBALL_PLAYER_STATS_FIELD_MAP
        elif sport == "soccer":
            field_map = ApiResponseMapper.SOCCER_PLAYER_STATS_FIELD_MAP
        elif sport == "volleyball":
            field_map = ApiResponseMapper.VOLLEYBALL_PLAYER_STATS_FIELD_MAP
        else:
            logger.warning(f"Unknown sport: {sport}, returning as-is")
            return api_stats

        # 매핑이 비어있으면 그대로 반환
        if not field_map:
            logger.debug(f"Field map for {sport} player stats is empty, returning as-is")
            return api_stats

        mapped = {}
        for api_field, internal_field in field_map.items():
            if api_field in api_stats:
                mapped[internal_field] = api_stats[api_field]

        # 매핑되지 않은 필드도 유지
        for key, value in api_stats.items():
            if key not in field_map and key not in mapped:
                mapped[key] = value

        return mapped

    @staticmethod
    def map_player_stats_list(api_response: Any, sport: str) -> List[Dict[str, Any]]:
        """선수 통계 목록 API 응답을 내부 포맷으로 변환.

        Args:
            api_response: 실제 API 응답
            sport: 스포츠 종목 (basketball, soccer, volleyball)

        Returns:
            선수 통계 목록
        """
        if isinstance(api_response, list):
            return [ApiResponseMapper.map_player_stats(stats, sport) for stats in api_response]

        if isinstance(api_response, dict):
            # 실제 API 구조: {"Data": {"list": [...]}} 또는 {"Data": [...]}
            if "Data" in api_response:
                data = api_response["Data"]
                if isinstance(data, dict) and "list" in data:
                    stats_list = data["list"]
                    if isinstance(stats_list, list):
                        return [ApiResponseMapper.map_player_stats(stats, sport) for stats in stats_list]
                elif isinstance(data, list):
                    return [ApiResponseMapper.map_player_stats(stats, sport) for stats in data]

            # 일반적인 응답 구조 시도
            for key in ["player_stats", "players", "data", "list"]:
                if key in api_response and isinstance(api_response[key], list):
                    return [ApiResponseMapper.map_player_stats(stats, sport) for stats in api_response[key]]

            logger.warning("Could not find player stats list in API response")
            return []

        return []

    @staticmethod
    def update_field_mappings(
        game_map: Optional[Dict[str, str]] = None,
        team_stats_map: Optional[Dict[str, str]] = None,
        player_stats_map: Optional[Dict[str, str]] = None
    ):
        """필드 매핑 테이블을 업데이트합니다.

        API_INTEGRATION.md를 작성한 후 이 메서드를 호출하여
        실제 필드 매핑을 설정할 수 있습니다.

        Args:
            game_map: 경기 데이터 필드 매핑
            team_stats_map: 팀 통계 필드 매핑
            player_stats_map: 선수 통계 필드 매핑
        """
        if game_map:
            ApiResponseMapper.GAME_FIELD_MAP.update(game_map)
            logger.info(f"Updated GAME_FIELD_MAP with {len(game_map)} mappings")

        if team_stats_map:
            ApiResponseMapper.TEAM_STATS_FIELD_MAP.update(team_stats_map)
            logger.info(f"Updated TEAM_STATS_FIELD_MAP with {len(team_stats_map)} mappings")

        if player_stats_map:
            ApiResponseMapper.PLAYER_STATS_FIELD_MAP.update(player_stats_map)
            logger.info(f"Updated PLAYER_STATS_FIELD_MAP with {len(player_stats_map)} mappings")
