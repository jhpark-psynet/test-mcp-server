"""Base Sports API Client with common HTTP request logic."""
from typing import Dict, Any, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
import logging
import httpx

from server.config import CONFIG
from server.errors import APIError, APIErrorCode

if TYPE_CHECKING:
    from server.services.sports.base.endpoints import SportEndpointConfig

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

    @property
    @abstractmethod
    def endpoint_config(self) -> "SportEndpointConfig":
        """Return the endpoint configuration for this sport.

        Must be implemented by subclasses to provide sport-specific
        endpoint mappings.

        Returns:
            SportEndpointConfig instance for this sport
        """
        pass

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Make async HTTP request to the Sports API.

        Args:
            endpoint: API endpoint path (e.g., "/data3V1/livescore/gameList")
            params: Request parameters

        Returns:
            API response (JSON)

        Raises:
            APIError: On HTTP error, timeout, or connection failure
        """
        # Add API key to parameters
        params_with_key = {**params, "auth_key": self.api_key}

        # Construct full URL
        url = self.base_url if not endpoint else f"{self.base_url}{endpoint}"

        logger.debug(f"Making async request to {url} with params: {params}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params_with_key)
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {url}")
            raise APIError(APIErrorCode.TIMEOUT, f"timeout={self.timeout}s") from e

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 404:
                raise APIError(APIErrorCode.NOT_FOUND, f"endpoint={endpoint}") from e
            elif e.response.status_code >= 500:
                raise APIError(APIErrorCode.SERVER_ERROR, f"status={e.response.status_code}") from e
            else:
                raise APIError(APIErrorCode.UNKNOWN, f"status={e.response.status_code}") from e

        except httpx.ConnectError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise APIError(APIErrorCode.CONNECTION_ERROR, str(e)) from e

        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}")
            raise APIError(APIErrorCode.UNKNOWN, str(e)) from e

    def _get_endpoint_for_operation(self, operation: str) -> str:
        """Get the API endpoint for a specific operation.

        Delegates to the sport-specific endpoint configuration.

        Args:
            operation: Operation name (e.g., 'games', 'team_stats', 'player_stats')

        Returns:
            Full endpoint path

        Raises:
            ValueError: If operation is not supported for this sport
        """
        return self.endpoint_config.get_endpoint(operation)

    def list_available_operations(self) -> Dict[str, str]:
        """List all available operations for this sport.

        Returns:
            Dict mapping operation names to endpoint paths
        """
        return self.endpoint_config.list_operations()
