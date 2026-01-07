"""Soccer-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


SOCCER_ENDPOINTS = SportEndpointConfig(
    sport_name="soccer",
    endpoints={
        # Team statistics
        "team_stats": f"{get_api_base_path()}/soccerTeamStat",

        # Player statistics (single game)
        "player_stats": f"{get_api_base_path()}/soccerPlayerStat",

        # Player season statistics
        "player_season_stats": f"{get_api_base_path()}/soccerPlayerSeasonStat",

        # Lineup
        "lineup": f"{get_api_base_path()}/soccerLineup",

        # Team rank (league standings)
        "team_rank": f"{get_api_base_path()}/soccerTeamRank",

        # Team vs team comparison (head-to-head records, recent form)
        "team_vs_list": f"{get_api_base_path()}/soccerVsInfo",
    },
    use_common={"games"},
)
