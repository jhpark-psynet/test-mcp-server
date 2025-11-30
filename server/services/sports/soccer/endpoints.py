"""Soccer-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


SOCCER_ENDPOINTS = SportEndpointConfig(
    sport_name="soccer",
    endpoints={
        # Team statistics
        "team_stats": f"{get_api_base_path()}/soccerTeamStat",

        # Player statistics
        "player_stats": f"{get_api_base_path()}/soccerPlayerStat",

        # Future extensibility examples (commented out):
        # "lineups": "/fifa/v2/lineups",
        # "possession": "/fifa/v2/possession",
        # "half_time_score": f"{get_api_base_path()}/soccerHalfTimeScore",
    },
    use_common={"games"},
)
