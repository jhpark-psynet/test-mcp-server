"""Base Response Mapper with common field mapping logic."""
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseResponseMapper(ABC):
    """Base class for API response mappers.

    Provides common response parsing and field mapping logic.
    Each sport-specific mapper should extend this class and provide field mappings.
    """

    @abstractmethod
    def get_game_field_map(self) -> Dict[str, str]:
        """Return field mapping for games list.

        Returns:
            Dict mapping API field names to internal field names
        """
        pass

    @abstractmethod
    def get_team_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for team stats.

        Returns:
            Dict mapping API field names to internal field names
        """
        pass

    @abstractmethod
    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for player stats.

        Returns:
            Dict mapping API field names to internal field names
        """
        pass

    def _apply_field_mapping(
        self,
        data: Dict[str, Any],
        field_map: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply field mapping to a single data item.

        Args:
            data: Original data from API
            field_map: Field mapping dictionary

        Returns:
            Mapped data
        """
        if not field_map:
            logger.debug("Field map is empty, returning data as-is")
            return data

        mapped = {}
        for api_field, internal_field in field_map.items():
            if api_field in data:
                mapped[internal_field] = data[api_field]

        # Keep unmapped fields as well
        for key, value in data.items():
            if key not in field_map and key not in mapped:
                mapped[key] = value

        return mapped

    def map_games_list(self, api_response: Any) -> List[Dict[str, Any]]:
        """Map games list API response to internal format.

        Args:
            api_response: Raw API response

        Returns:
            List of mapped game data
        """
        # Handle list response
        if isinstance(api_response, list):
            field_map = self.get_game_field_map()
            return [self._apply_field_mapping(game, field_map) for game in api_response]

        # Handle dict response
        if isinstance(api_response, dict):
            # Try Data.list structure first (actual API structure)
            if "Data" in api_response and isinstance(api_response["Data"], dict):
                games_list = api_response["Data"].get("list", [])
                if isinstance(games_list, list):
                    logger.debug(f"Found {len(games_list)} games in 'Data.list'")
                    field_map = self.get_game_field_map()
                    return [self._apply_field_mapping(game, field_map) for game in games_list]

            # Try common field names
            for key in ["games", "data", "results", "items", "list"]:
                if key in api_response and isinstance(api_response[key], list):
                    logger.debug(f"Found games list in '{key}' field")
                    field_map = self.get_game_field_map()
                    return [self._apply_field_mapping(game, field_map) for game in api_response[key]]

            logger.warning("Could not find games list in API response")
            return []

        logger.error(f"Unexpected API response type: {type(api_response)}")
        return []

    def map_team_stats_list(self, api_response: Any) -> List[Dict[str, Any]]:
        """Map team stats list API response to internal format.

        Args:
            api_response: Raw API response

        Returns:
            List of mapped team stats [home_team, away_team]
        """
        # Handle list response
        if isinstance(api_response, list):
            field_map = self.get_team_stats_field_map()
            return [self._apply_field_mapping(stats, field_map) for stats in api_response]

        # Handle dict response
        if isinstance(api_response, dict):
            # Try Data.list or Data as list
            if "Data" in api_response:
                data = api_response["Data"]
                if isinstance(data, dict) and "list" in data:
                    stats_list = data["list"]
                    if isinstance(stats_list, list):
                        field_map = self.get_team_stats_field_map()
                        return [self._apply_field_mapping(stats, field_map) for stats in stats_list]
                elif isinstance(data, list):
                    field_map = self.get_team_stats_field_map()
                    return [self._apply_field_mapping(stats, field_map) for stats in data]

            # Try common field names
            for key in ["team_stats", "teams", "data", "list"]:
                if key in api_response and isinstance(api_response[key], list):
                    field_map = self.get_team_stats_field_map()
                    return [self._apply_field_mapping(stats, field_map) for stats in api_response[key]]

            logger.warning("Could not find team stats list in API response")
            return []

        return []

    def map_player_stats_list(self, api_response: Any) -> List[Dict[str, Any]]:
        """Map player stats list API response to internal format.

        Args:
            api_response: Raw API response

        Returns:
            List of mapped player stats
        """
        # Handle list response
        if isinstance(api_response, list):
            field_map = self.get_player_stats_field_map()
            return [self._apply_field_mapping(stats, field_map) for stats in api_response]

        # Handle dict response
        if isinstance(api_response, dict):
            # Try Data.list or Data as list
            if "Data" in api_response:
                data = api_response["Data"]
                if isinstance(data, dict) and "list" in data:
                    stats_list = data["list"]
                    if isinstance(stats_list, list):
                        field_map = self.get_player_stats_field_map()
                        return [self._apply_field_mapping(stats, field_map) for stats in stats_list]
                elif isinstance(data, list):
                    field_map = self.get_player_stats_field_map()
                    return [self._apply_field_mapping(stats, field_map) for stats in data]

            # Try common field names
            for key in ["player_stats", "players", "data", "list"]:
                if key in api_response and isinstance(api_response[key], list):
                    field_map = self.get_player_stats_field_map()
                    return [self._apply_field_mapping(stats, field_map) for stats in api_response[key]]

            logger.warning("Could not find player stats list in API response")
            return []

        return []
