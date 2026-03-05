"""Baseball-specific endpoint configuration."""
from server.services.sports.base.endpoints import SportEndpointConfig, get_api_base_path


BASEBALL_ENDPOINTS = SportEndpointConfig(
    sport_name="baseball",
    endpoints={
        # All-in-one game info API
        "total_info": f"{get_api_base_path()}/baseballGameTotalInfo",
    },
    use_common={"games"},
)
