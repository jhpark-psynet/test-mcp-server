"""Pydantic 스키마 정의."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class WidgetToolInput(BaseModel):
    """Widget tool input schema."""
    message: str = Field(..., description="Message to pass to the widget.")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class GetGamesBySportInput(BaseModel):
    """Get games by sport tool input schema."""
    date: str = Field(
        ...,
        description="Date to query (YYYYMMDD format, e.g., '20251118')."
    )
    sport: str = Field(
        ...,
        description="Sport type to query.",
        pattern="^(basketball|soccer|volleyball|football)$"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force refresh from API, ignoring cache. Use when data seems stale."
    )
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class GetGameDetailsInput(BaseModel):
    """Get game details tool input schema (widget-based)."""
    game_id: str = Field(
        ...,
        description="Game ID to query (from get_games_by_sport result)."
    )
    date: str = Field(
        ...,
        description="Date of the game (YYYYMMDD format, same as used in get_games_by_sport)."
    )
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


# JSON schemas for MCP tools
WIDGET_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "description": "Message to pass to the widget.",
        }
    },
    "required": ["message"],
    "additionalProperties": False,
}

GET_GAMES_BY_SPORT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "date": {
            "type": "string",
            "description": "Date to query (YYYYMMDD format, e.g., '20251118')."
        },
        "sport": {
            "type": "string",
            "enum": ["basketball", "soccer", "volleyball", "football"],
            "description": "Sport type to query."
        },
        "force_refresh": {
            "type": "boolean",
            "description": "Force refresh from API, ignoring cache. Use when data seems stale.",
            "default": False
        }
    },
    "required": ["date", "sport"],
    "additionalProperties": False,
}

GET_GAME_DETAILS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "game_id": {
            "type": "string",
            "description": "Game ID to query (from get_games_by_sport result)."
        },
        "date": {
            "type": "string",
            "description": "Date of the game (YYYYMMDD format, same as used in get_games_by_sport)."
        }
    },
    "required": ["game_id", "date"],
    "additionalProperties": False,
}
