"""Soccer-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


SOCCER_ENDPOINTS = SportEndpointConfig(
    sport_name="soccer",
    endpoints={
        # Team statistics
        "team_stats": f"{get_api_base_path()}/soccerTeamStat",

        # Player statistics
        "player_stats": f"{get_api_base_path()}/soccerPlayerStat",

        # Lineup
        "lineup": f"{get_api_base_path()}/soccerLineup",
    },
    use_common={"games"},
)
