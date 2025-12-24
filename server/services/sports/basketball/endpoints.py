"""Basketball-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


BASKETBALL_ENDPOINTS = SportEndpointConfig(
    sport_name="basketball",
    endpoints={
        # Team statistics
        "team_stats": f"{get_api_base_path()}/basketballTeamStat",

        # Player statistics
        "player_stats": f"{get_api_base_path()}/basketballPlayerStat",

        # Lineup (starting lineup + bench)
        "lineup": f"{get_api_base_path()}/basketballLineup",

        # Team rankings by league/season
        "team_rank": f"{get_api_base_path()}/basketballTeamRank",

        # Team vs team comparison (recent games, records, stats)
        "team_vs_list": f"{get_api_base_path()}/basketballVsInfo",

        # Future extensibility examples (commented out):
        # "box_score": "/nba/v1/boxscore",
        # "play_by_play": "/nba/v1/playbyplay",
        # "quarter_scores": f"{get_api_base_path()}/basketballQuarterScore",
    },
    # Use common endpoints for these operations
    use_common={"games"},
)
