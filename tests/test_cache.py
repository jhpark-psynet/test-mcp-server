"""캐시 모듈 단위 테스트."""
import pytest
from server.services.cache import (
    cache_games,
    get_cached_games,
    find_game_in_cache,
    clear_cache,
    invalidate_cache,
    get_cache_info,
    _is_valid_game,
    REQUIRED_GAME_FIELDS,
)


@pytest.fixture(autouse=True)
def clean_cache():
    """각 테스트 전후로 캐시 정리."""
    clear_cache()
    yield
    clear_cache()


class TestGameValidation:
    """게임 데이터 검증 테스트."""

    def test_valid_game_with_all_fields(self):
        """모든 필수 필드가 있으면 유효."""
        game = {
            "game_id": "G001",
            "home_team_name": "TeamA",
            "away_team_name": "TeamB",
        }
        assert _is_valid_game(game) is True

    def test_invalid_game_missing_game_id(self):
        """game_id 누락 시 무효."""
        game = {"home_team_name": "TeamA", "away_team_name": "TeamB"}
        assert _is_valid_game(game) is False

    def test_invalid_game_missing_home_team(self):
        """home_team_name 누락 시 무효."""
        game = {"game_id": "G001", "away_team_name": "TeamB"}
        assert _is_valid_game(game) is False

    def test_invalid_game_empty_field(self):
        """필수 필드가 빈 문자열이면 무효."""
        game = {
            "game_id": "G001",
            "home_team_name": "",
            "away_team_name": "TeamB",
        }
        assert _is_valid_game(game) is False

    def test_invalid_game_whitespace_field(self):
        """필수 필드가 공백만 있으면 무효."""
        game = {
            "game_id": "G001",
            "home_team_name": "   ",
            "away_team_name": "TeamB",
        }
        assert _is_valid_game(game) is False


class TestCacheGames:
    """cache_games 함수 테스트."""

    def test_cache_stores_valid_games(self):
        """유효한 게임 목록이 캐시에 저장됨."""
        games = [{
            "game_id": "G001",
            "home_team_name": "TeamA",
            "away_team_name": "TeamB",
        }]
        result = cache_games("20241222", "basketball", games)

        assert result is True
        assert get_cached_games("20241222", "basketball") == games

    def test_cache_returns_false_for_empty_list(self):
        """빈 목록은 캐시되지 않고 False 반환."""
        result = cache_games("20241222", "basketball", [])

        assert result is False
        assert get_cached_games("20241222", "basketball") is None

    def test_cache_returns_false_for_all_invalid_games(self):
        """모든 게임이 무효하면 캐시되지 않음."""
        invalid_games = [
            {"game_id": "G001"},  # home_team_name, away_team_name 누락
            {"home_team_name": "TeamA"},  # game_id, away_team_name 누락
        ]
        result = cache_games("20241222", "basketball", invalid_games)

        assert result is False
        assert get_cached_games("20241222", "basketball") is None

    def test_cache_filters_invalid_games(self):
        """유효한 게임만 필터링되어 캐시됨."""
        mixed_games = [
            {"game_id": "G001", "home_team_name": "TeamA", "away_team_name": "TeamB"},  # 유효
            {"game_id": "G002"},  # 무효
        ]
        result = cache_games("20241222", "basketball", mixed_games)

        assert result is True
        cached = get_cached_games("20241222", "basketball")
        assert len(cached) == 1
        assert cached[0]["game_id"] == "G001"

    def test_cache_key_isolation(self):
        """다른 날짜/스포츠는 별도 키로 저장."""
        games1 = [{"game_id": "G001", "home_team_name": "A", "away_team_name": "B"}]
        games2 = [{"game_id": "G002", "home_team_name": "C", "away_team_name": "D"}]

        cache_games("20241222", "basketball", games1)
        cache_games("20241223", "basketball", games2)

        assert get_cached_games("20241222", "basketball")[0]["game_id"] == "G001"
        assert get_cached_games("20241223", "basketball")[0]["game_id"] == "G002"


class TestInvalidateCache:
    """invalidate_cache 함수 테스트."""

    def test_invalidate_existing_cache(self):
        """존재하는 캐시 무효화."""
        games = [{"game_id": "G001", "home_team_name": "A", "away_team_name": "B"}]
        cache_games("20241222", "basketball", games)

        result = invalidate_cache("20241222", "basketball")

        assert result is True
        assert get_cached_games("20241222", "basketball") is None

    def test_invalidate_nonexistent_cache(self):
        """존재하지 않는 캐시 무효화 시 False."""
        result = invalidate_cache("20241222", "basketball")
        assert result is False

    def test_invalidate_only_target_key(self):
        """특정 키만 무효화되고 다른 키는 유지."""
        games1 = [{"game_id": "G001", "home_team_name": "A", "away_team_name": "B"}]
        games2 = [{"game_id": "G002", "home_team_name": "C", "away_team_name": "D"}]
        cache_games("20241222", "basketball", games1)
        cache_games("20241223", "basketball", games2)

        invalidate_cache("20241222", "basketball")

        assert get_cached_games("20241222", "basketball") is None
        assert get_cached_games("20241223", "basketball") is not None


class TestFindGameInCache:
    """find_game_in_cache 함수 테스트."""

    def test_find_existing_game(self):
        """캐시에서 특정 게임 찾기."""
        games = [
            {"game_id": "G001", "home_team_name": "TeamA", "away_team_name": "TeamX"},
            {"game_id": "G002", "home_team_name": "TeamB", "away_team_name": "TeamY"},
        ]
        cache_games("20241222", "basketball", games)

        result = find_game_in_cache("20241222", "basketball", "G002")
        assert result is not None
        assert result["home_team_name"] == "TeamB"

    def test_find_nonexistent_game(self):
        """존재하지 않는 게임 찾기."""
        games = [{"game_id": "G001", "home_team_name": "A", "away_team_name": "B"}]
        cache_games("20241222", "basketball", games)

        result = find_game_in_cache("20241222", "basketball", "NOTFOUND")
        assert result is None

    def test_find_in_empty_cache(self):
        """빈 캐시에서 찾기."""
        result = find_game_in_cache("20241222", "basketball", "G001")
        assert result is None


class TestClearCache:
    """clear_cache 함수 테스트."""

    def test_clear_removes_all_entries(self):
        """캐시 정리 후 모든 항목 삭제됨."""
        games = [{"game_id": "G001", "home_team_name": "A", "away_team_name": "B"}]
        cache_games("20241222", "basketball", games)
        cache_games("20241223", "soccer", games)

        clear_cache()

        assert get_cached_games("20241222", "basketball") is None
        assert get_cached_games("20241223", "soccer") is None


class TestCacheInfo:
    """get_cache_info 함수 테스트."""

    def test_cache_info_returns_stats(self):
        """캐시 상태 정보 반환."""
        games = [{"game_id": "G001", "home_team_name": "A", "away_team_name": "B"}]
        cache_games("20241222", "basketball", games)

        info = get_cache_info()
        assert info["current_size"] == 1
        assert info["max_size"] > 0
        assert info["ttl"] > 0
