"""Unit tests for endpoint configuration."""
import pytest
from unittest.mock import patch

from server.services.sports.base.endpoints import (
    CommonEndpoints,
    SportEndpointConfig,
    COMMON_ENDPOINTS,
    get_api_base_path,
)
from server.services.sports.basketball.endpoints import BASKETBALL_ENDPOINTS
from server.services.sports.soccer.endpoints import SOCCER_ENDPOINTS
from server.services.sports.volleyball.endpoints import VOLLEYBALL_ENDPOINTS
from server.services.sports.football.endpoints import FOOTBALL_ENDPOINTS


class TestGetApiBasePath:
    """Tests for environment-based path resolution."""

    @patch("server.services.sports.base.endpoints.CONFIG")
    def test_production_path(self, mock_config):
        """Production environment uses standard path."""
        mock_config.environment = "production"
        # Need to reimport to pick up patched CONFIG
        from server.services.sports.base import endpoints
        result = endpoints.get_api_base_path()
        assert result == "/data3V1/livescore"
        assert "dev" not in result

    @patch("server.services.sports.base.endpoints.CONFIG")
    def test_development_path(self, mock_config):
        """Development environment uses dev path."""
        mock_config.environment = "development"
        from server.services.sports.base import endpoints
        result = endpoints.get_api_base_path()
        assert "dev" in result


class TestCommonEndpoints:
    """Tests for shared endpoint definitions."""

    def test_games_endpoint_exists(self):
        """Games endpoint is defined."""
        assert COMMON_ENDPOINTS.games is not None
        assert "gameList" in COMMON_ENDPOINTS.games

    def test_common_endpoints_immutable(self):
        """CommonEndpoints is frozen (immutable)."""
        with pytest.raises(AttributeError):
            COMMON_ENDPOINTS.games = "/new/path"


class TestSportEndpointConfig:
    """Tests for SportEndpointConfig class."""

    def test_get_common_endpoint(self):
        """Can retrieve common endpoint via use_common."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"custom": "/test/custom"},
            use_common={"games"}
        )
        result = config.get_endpoint("games")
        assert result == COMMON_ENDPOINTS.games

    def test_get_sport_specific_endpoint(self):
        """Can retrieve sport-specific endpoint."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"team_stats": "/test/team-stats"},
            use_common=set()
        )
        assert config.get_endpoint("team_stats") == "/test/team-stats"

    def test_sport_specific_overrides_common(self):
        """Sport-specific endpoint takes priority over common."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"games": "/custom/games"},
            use_common={"games"}
        )
        # Sport-specific is checked first
        assert config.get_endpoint("games") == "/custom/games"

    def test_unknown_operation_raises_error(self):
        """Unknown operation raises ValueError with helpful message."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"op1": "/path1"}
        )
        with pytest.raises(ValueError, match="not supported"):
            config.get_endpoint("unknown_op")
        with pytest.raises(ValueError, match="test"):
            config.get_endpoint("unknown_op")

    def test_list_operations(self):
        """list_operations returns all available operations."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"team_stats": "/test/team"},
            use_common={"games"}
        )
        ops = config.list_operations()
        assert "team_stats" in ops
        assert "games" in ops
        assert "[common]" in ops["games"]

    def test_has_operation(self):
        """has_operation correctly checks availability."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"team_stats": "/test/team"},
            use_common={"games"}
        )
        assert config.has_operation("team_stats") is True
        assert config.has_operation("games") is True
        assert config.has_operation("unknown") is False


class TestSportEndpointConfigEdgeCases:
    """Edge case tests for SportEndpointConfig."""

    def test_empty_endpoints_and_empty_use_common(self):
        """Empty config raises error for any operation."""
        config = SportEndpointConfig(
            sport_name="empty",
            endpoints={},
            use_common=set()
        )
        with pytest.raises(ValueError, match="not supported"):
            config.get_endpoint("games")
        with pytest.raises(ValueError, match="not supported"):
            config.get_endpoint("team_stats")
        # has_operation returns False, not error
        assert config.has_operation("games") is False

    def test_use_common_with_nonexistent_common_endpoint(self):
        """use_common references operation not in CommonEndpoints."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={},
            use_common={"nonexistent_operation"}
        )
        with pytest.raises(ValueError, match="not supported"):
            config.get_endpoint("nonexistent_operation")

    def test_empty_string_operation(self):
        """Empty string operation raises error."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"valid": "/path"},
            use_common={"games"}
        )
        with pytest.raises(ValueError, match="not supported"):
            config.get_endpoint("")

    def test_none_in_endpoints_dict(self):
        """None value in endpoints dict is returned as-is."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"bad_endpoint": None},
            use_common=set()
        )
        result = config.get_endpoint("bad_endpoint")
        assert result is None

    def test_whitespace_operation_name(self):
        """Whitespace-only operation name raises error."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"valid": "/path"},
            use_common={"games"}
        )
        with pytest.raises(ValueError, match="not supported"):
            config.get_endpoint("   ")

    def test_case_sensitivity(self):
        """Operation names are case-sensitive."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"Team_Stats": "/path/upper"},
            use_common=set()
        )
        assert config.get_endpoint("Team_Stats") == "/path/upper"
        with pytest.raises(ValueError):
            config.get_endpoint("team_stats")
        with pytest.raises(ValueError):
            config.get_endpoint("TEAM_STATS")

    def test_special_characters_in_operation_name(self):
        """Operation names with special characters work if defined."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"team-stats": "/path/with-dash", "stats.v2": "/path/with.dot"},
            use_common=set()
        )
        assert config.get_endpoint("team-stats") == "/path/with-dash"
        assert config.get_endpoint("stats.v2") == "/path/with.dot"

    def test_duplicate_in_endpoints_and_use_common_priority(self):
        """When same operation in both, endpoints takes priority."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"games": "/custom/games/path"},
            use_common={"games"}
        )
        result = config.get_endpoint("games")
        assert result == "/custom/games/path"
        assert result != COMMON_ENDPOINTS.games

    def test_list_operations_with_override(self):
        """list_operations shows overridden endpoint, not common."""
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"games": "/custom/games"},
            use_common={"games"}
        )
        ops = config.list_operations()
        assert ops["games"] == "/custom/games"
        assert "[common]" not in ops["games"]

    def test_error_message_shows_available_operations(self):
        """Error message lists available operations."""
        config = SportEndpointConfig(
            sport_name="test_sport",
            endpoints={"op1": "/p1", "op2": "/p2"},
            use_common={"games"}
        )
        with pytest.raises(ValueError) as exc_info:
            config.get_endpoint("invalid")
        error_msg = str(exc_info.value)
        assert "test_sport" in error_msg
        assert "op1" in error_msg or "op2" in error_msg or "games" in error_msg

    def test_very_long_endpoint_path(self):
        """Very long endpoint paths are handled."""
        long_path = "/api/v1/" + "a" * 500 + "/endpoint"
        config = SportEndpointConfig(
            sport_name="test",
            endpoints={"long_op": long_path},
            use_common=set()
        )
        assert config.get_endpoint("long_op") == long_path

    def test_unicode_in_sport_name(self):
        """Unicode characters in sport name work."""
        config = SportEndpointConfig(
            sport_name="축구",
            endpoints={"team_stats": "/path"},
            use_common=set()
        )
        assert config.sport_name == "축구"
        with pytest.raises(ValueError, match="축구"):
            config.get_endpoint("invalid")


class TestBasketballEndpoints:
    """Tests for basketball endpoint configuration."""

    def test_sport_name(self):
        """Sport name is basketball."""
        assert BASKETBALL_ENDPOINTS.sport_name == "basketball"

    def test_required_operations_exist(self):
        """Required operations are defined."""
        for op in ["games", "team_stats", "player_stats"]:
            assert BASKETBALL_ENDPOINTS.has_operation(op)

    def test_team_stats_endpoint_contains_basketball(self):
        """Team stats endpoint is basketball-specific."""
        endpoint = BASKETBALL_ENDPOINTS.get_endpoint("team_stats")
        assert "basketball" in endpoint.lower()

    def test_uses_common_games_endpoint(self):
        """Games uses common endpoint."""
        assert "games" in BASKETBALL_ENDPOINTS.use_common


class TestSoccerEndpoints:
    """Tests for soccer endpoint configuration."""

    def test_sport_name(self):
        assert SOCCER_ENDPOINTS.sport_name == "soccer"

    def test_required_operations_exist(self):
        for op in ["games", "team_stats", "player_stats"]:
            assert SOCCER_ENDPOINTS.has_operation(op)


class TestVolleyballEndpoints:
    """Tests for volleyball endpoint configuration."""

    def test_sport_name(self):
        assert VOLLEYBALL_ENDPOINTS.sport_name == "volleyball"

    def test_required_operations_exist(self):
        for op in ["games", "team_stats", "player_stats"]:
            assert VOLLEYBALL_ENDPOINTS.has_operation(op)


class TestFootballEndpoints:
    """Tests for football endpoint configuration."""

    def test_sport_name(self):
        assert FOOTBALL_ENDPOINTS.sport_name == "football"

    def test_required_operations_exist(self):
        for op in ["games", "team_stats", "player_stats"]:
            assert FOOTBALL_ENDPOINTS.has_operation(op)


class TestAllSportsConsistency:
    """Cross-sport consistency tests."""

    @pytest.mark.parametrize("config", [
        BASKETBALL_ENDPOINTS,
        SOCCER_ENDPOINTS,
        VOLLEYBALL_ENDPOINTS,
        FOOTBALL_ENDPOINTS,
    ])
    def test_all_have_required_operations(self, config):
        """All sports have the required operations."""
        required = ["games", "team_stats", "player_stats"]
        for op in required:
            assert config.has_operation(op), f"{config.sport_name} missing {op}"

    @pytest.mark.parametrize("config", [
        BASKETBALL_ENDPOINTS,
        SOCCER_ENDPOINTS,
        VOLLEYBALL_ENDPOINTS,
        FOOTBALL_ENDPOINTS,
    ])
    def test_endpoints_start_with_slash(self, config):
        """All endpoint paths start with /."""
        for op in ["team_stats", "player_stats"]:
            endpoint = config.get_endpoint(op)
            assert endpoint.startswith("/"), f"{config.sport_name}.{op}: {endpoint}"
