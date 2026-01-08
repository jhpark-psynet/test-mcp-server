"""Tests for client endpoint integration with mock injection."""
import pytest
from unittest.mock import patch, PropertyMock

from server.services.sports.base.endpoints import SportEndpointConfig
from server.services.sports.basketball.client import BasketballClient
from server.services.sports.soccer.client import SoccerClient
from server.services.sports import SportsClientFactory


class TestClientEndpointIntegration:
    """Test clients use endpoint configuration correctly."""

    def test_basketball_client_has_endpoint_config(self):
        """Basketball client exposes endpoint_config property."""
        client = BasketballClient()
        config = client.endpoint_config
        assert config.sport_name == "basketball"

    def test_client_get_endpoint_for_operation(self):
        """Client._get_endpoint_for_operation uses config."""
        client = BasketballClient()
        endpoint = client._get_endpoint_for_operation("team_stats")
        assert "basketball" in endpoint.lower()
        assert "TeamStat" in endpoint

    def test_client_list_available_operations(self):
        """Client can list all available operations."""
        client = BasketballClient()
        ops = client.list_available_operations()
        assert "games" in ops
        assert "team_stats" in ops
        assert "player_stats" in ops


class TestMockEndpointInjection:
    """Test mock endpoint injection for testing."""

    def test_inject_custom_endpoint_config(self):
        """Can inject custom endpoint config for testing."""
        mock_config = SportEndpointConfig(
            sport_name="test_basketball",
            endpoints={
                "games": "/test/games",
                "team_stats": "/test/team-stats",
                "player_stats": "/test/player-stats",
            },
            use_common=set()
        )

        client = BasketballClient()

        with patch.object(
            type(client), 'endpoint_config',
            new_callable=PropertyMock,
            return_value=mock_config
        ):
            endpoint = client._get_endpoint_for_operation("team_stats")
            assert endpoint == "/test/team-stats"

    def test_endpoint_isolation_between_clients(self):
        """Modifying one client's endpoints doesn't affect others."""
        basketball = BasketballClient()
        soccer = SoccerClient()

        bb_endpoint = basketball._get_endpoint_for_operation("team_stats")
        sc_endpoint = soccer._get_endpoint_for_operation("team_stats")

        assert "basketball" in bb_endpoint.lower()
        assert "soccer" in sc_endpoint.lower()
        assert bb_endpoint != sc_endpoint


class TestFactoryWithRegistry:
    """Test factory registry pattern."""

    def test_list_sports(self):
        """Factory lists all registered sports."""
        sports = SportsClientFactory.list_sports()
        assert "basketball" in sports
        assert "soccer" in sports
        assert "volleyball" in sports

    def test_create_all_sports(self):
        """Factory creates all registered sports."""
        for sport in SportsClientFactory.list_sports():
            client = SportsClientFactory.create_client(sport)
            assert client.get_sport_name() == sport

    def test_invalid_sport_error_message(self):
        """Invalid sport gives helpful error."""
        with pytest.raises(ValueError) as exc_info:
            SportsClientFactory.create_client("cricket")
        assert "cricket" in str(exc_info.value)
        assert "basketball" in str(exc_info.value)

    def test_register_new_sport(self):
        """Can dynamically register new sport."""
        class MockCricketClient:
            def get_sport_name(self):
                return "cricket"

        SportsClientFactory.register("cricket", MockCricketClient)

        try:
            assert "cricket" in SportsClientFactory.list_sports()
            client = SportsClientFactory.create_client("cricket")
            assert client.get_sport_name() == "cricket"
        finally:
            SportsClientFactory.unregister("cricket")

        assert "cricket" not in SportsClientFactory.list_sports()
