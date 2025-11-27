"""Soccer-specific response mapper."""
from typing import Dict
from server.services.sports.base.mapper import BaseResponseMapper


class SoccerMapper(BaseResponseMapper):
    """Response mapper for Soccer API."""

    def get_game_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer games list."""
        return {
            "GAME_ID": "game_id",
            "LEAGUE_NAME": "league_name",
            "MATCH_DATE": "match_date",
            "MATCH_TIME": "match_time",
            "HOME_TEAM_ID": "home_team_id",
            "AWAY_TEAM_ID": "away_team_id",
            "HOME_TEAM_NAME": "home_team_name",
            "AWAY_TEAM_NAME": "away_team_name",
            "HOME_SCORE": "home_score",
            "AWAY_SCORE": "away_score",
            "STATE": "state",
            "ARENA_NAME": "arena_name",
            "COMPE": "compe",
        }

    def get_team_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer team stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}

    def get_player_stats_field_map(self) -> Dict[str, str]:
        """Return field mapping for soccer player stats."""
        # TODO: Fill with actual API field mappings after testing real endpoint
        return {}
