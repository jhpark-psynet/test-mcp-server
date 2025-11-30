"""Basketball-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


BASKETBALL_ENDPOINTS = SportEndpointConfig(
    sport_name="basketball",
    endpoints={
        # Team statistics
        "team_stats": f"{get_api_base_path()}/basketballTeamStat",

        # Player statistics
        "player_stats": f"{get_api_base_path()}/basketballPlayerStat",

        # Future extensibility examples (commented out):
        # "box_score": "/nba/v1/boxscore",
        # "play_by_play": "/nba/v1/playbyplay",
        # "standings": "/nba/v1/standings",
        # "quarter_scores": f"{get_api_base_path()}/basketballQuarterScore",
    },
    # Use common endpoints for these operations
    use_common={"games"},
)
