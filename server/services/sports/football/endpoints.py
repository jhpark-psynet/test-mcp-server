"""Football-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


FOOTBALL_ENDPOINTS = SportEndpointConfig(
    sport_name="football",
    endpoints={
        # Team statistics
        "team_stats": f"{get_api_base_path()}/footballTeamStat",

        # Player statistics
        "player_stats": f"{get_api_base_path()}/footballPlayerStat",

        # Future extensibility examples (commented out):
        # "quarter_scores": f"{get_api_base_path()}/footballQuarterScore",
        # "drive_chart": "/nfl/v1/drivechart",
    },
    use_common={"games"},
)
