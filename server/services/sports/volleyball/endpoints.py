"""Volleyball-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


VOLLEYBALL_ENDPOINTS = SportEndpointConfig(
    sport_name="volleyball",
    endpoints={
        # Team statistics
        "team_stats": f"{get_api_base_path()}/volleyballTeamStat",

        # Player statistics
        "player_stats": f"{get_api_base_path()}/volleyballPlayerStat",

        # Future extensibility examples (commented out):
        # "set_scores": f"{get_api_base_path()}/volleyballSetScore",
    },
    use_common={"games"},
)
