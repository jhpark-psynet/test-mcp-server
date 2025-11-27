"""Base Sports API Client with common HTTP request logic."""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
import httpx

from server.config import CONFIG

logger = logging.getLogger(__name__)


class BaseSportsClient(ABC):
    """Base class for Sports API clients.

    Provides common HTTP request logic, authentication, and error handling.
    Each sport-specific client should extend this class.
    """

    def __init__(self):
        """Initialize base sports API client."""
        self.use_mock = CONFIG.use_mock_sports_data
        self.base_url = CONFIG.sports_api_base_url
        self.api_key = CONFIG.sports_api_key
        self.timeout = CONFIG.sports_api_timeout_s

        if self.use_mock:
            logger.info(f"{self.__class__.__name__} initialized with MOCK data")
        elif CONFIG.has_sports_api:
            logger.info(f"{self.__class__.__name__} initialized with REAL API: {self.base_url}")
        else:
            logger.warning(
                f"{self.__class__.__name__}: Real API requested but not configured. "
                "Falling back to mock data."
            )
            self.use_mock = True

    @abstractmethod
    def get_sport_name(self) -> str:
        """Return the sport name (e.g., 'basketball', 'soccer', 'volleyball').

        Must be implemented by subclasses.
        """
        pass

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Make HTTP request to the Sports API.

        Args:
            endpoint: API endpoint path (e.g., "/data3V1/livescore/gameList")
            params: Request parameters

        Returns:
            API response (JSON)

        Raises:
            ValueError: HTTP error, timeout, or other errors
        """
        # Add API key to parameters
        params_with_key = {**params, "auth_key": self.api_key}

        # Construct full URL
        url = self.base_url if not endpoint else f"{self.base_url}{endpoint}"

        logger.debug(f"Making request to {url} with params: {params}")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params_with_key)
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {url}")
            raise ValueError(f"API request timed out after {self.timeout}s") from e

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 404:
                raise ValueError(f"API endpoint not found: {url}") from e
            elif e.response.status_code >= 500:
                raise ValueError(f"API server error: {e.response.status_code}") from e
            else:
                raise ValueError(f"API request failed: {e.response.status_code}") from e

        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}")
            raise ValueError(f"API request failed: {str(e)}") from e

    def _get_endpoint_for_operation(self, operation: str) -> str:
        """Get the API endpoint for a specific operation.

        Args:
            operation: One of 'games', 'team_stats', 'player_stats'

        Returns:
            Full endpoint path
        """
        sport = self.get_sport_name()

        if operation == "games":
            return "/data3V1/livescore/gameList"
        elif operation == "team_stats":
            return f"/data3V1/livescore/{sport}TeamStat"
        elif operation == "player_stats":
            return f"/data3V1/livescore/{sport}PlayerStat"
        else:
            raise ValueError(f"Unknown operation: {operation}")
