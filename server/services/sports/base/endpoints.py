"""Common endpoint definitions shared across all sports."""
from typing import Dict, Set
from dataclasses import dataclass, field

from server.config import CONFIG


def get_api_base_path() -> str:
    """Get API base path based on environment.

    Returns:
        Base path prefix for API endpoints
    """
    if CONFIG.environment == "production":
        return "/data3V1/livescore"
    else:
        # Development and all other environments
        return "/dev/data3V1/livescore"


@dataclass(frozen=True)
class CommonEndpoints:
    """Endpoints shared by all sports.

    These endpoints use the same path regardless of sport type.
    Frozen dataclass ensures immutability.
    """

    @property
    def games(self) -> str:
        """Game list endpoint - shared across all sports."""
        return f"{get_api_base_path()}/gameList"


# Singleton instance
COMMON_ENDPOINTS = CommonEndpoints()


@dataclass
class SportEndpointConfig:
    """Configuration for sport-specific endpoints.

    Attributes:
        sport_name: The sport identifier (e.g., 'basketball', 'soccer')
        endpoints: Dict mapping operation names to endpoint paths
        use_common: Set of operation names that should use common endpoints
    """
    sport_name: str
    endpoints: Dict[str, str] = field(default_factory=dict)
    use_common: Set[str] = field(default_factory=lambda: {"games"})

    def get_endpoint(self, operation: str) -> str:
        """Get endpoint for an operation.

        Priority:
        1. Sport-specific endpoint (if defined in endpoints dict)
        2. Common endpoint (if operation in use_common)
        3. Raise ValueError

        Args:
            operation: Operation name (e.g., 'team_stats', 'games')

        Returns:
            Full endpoint path

        Raises:
            ValueError: If operation is not supported
        """
        # Check sport-specific endpoints first
        if operation in self.endpoints:
            return self.endpoints[operation]

        # Check common endpoints
        if operation in self.use_common:
            if hasattr(COMMON_ENDPOINTS, operation):
                return getattr(COMMON_ENDPOINTS, operation)

        # Build helpful error message
        available = list(self.endpoints.keys()) + list(self.use_common)
        raise ValueError(
            f"Operation '{operation}' not supported for {self.sport_name}. "
            f"Available: {sorted(available)}"
        )

    def list_operations(self) -> Dict[str, str]:
        """List all available operations and their endpoints.

        Returns:
            Dict mapping operation names to endpoint paths (with [common] prefix for shared)
        """
        result = {}

        # Common endpoints
        for op in self.use_common:
            if hasattr(COMMON_ENDPOINTS, op):
                result[op] = f"[common] {getattr(COMMON_ENDPOINTS, op)}"

        # Sport-specific endpoints (may override common)
        for op, endpoint in self.endpoints.items():
            result[op] = endpoint

        return result

    def has_operation(self, operation: str) -> bool:
        """Check if an operation is supported.

        Args:
            operation: Operation name to check

        Returns:
            True if operation is available
        """
        if operation in self.endpoints:
            return True
        if operation in self.use_common and hasattr(COMMON_ENDPOINTS, operation):
            return True
        return False
