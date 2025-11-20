"""Pydantic 스키마 정의."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class WidgetToolInput(BaseModel):
    """Widget tool input schema."""
    message: str = Field(..., description="Message to pass to the widget.")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class ExternalToolInput(BaseModel):
    """External API fetch tool input schema."""
    query: str = Field(
        ...,
        description="API endpoint path to fetch (e.g., '/users' or '/search')."
    )
    response_mode: str = Field(
        default="text",
        description="Response mode: 'text' for formatted text output, 'widget' for interactive UI.",
        pattern="^(text|widget)$"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Query parameters or request body for the API call."
    )
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
        pattern="^(basketball|baseball|football)$"
    )
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class GetGameDetailsInput(BaseModel):
    """Get game details tool input schema (widget-based)."""
    game_id: str = Field(
        ...,
        description="Game ID to query (from get_games_by_sport result)."
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

EXTERNAL_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "API endpoint path to fetch (e.g., '/posts/1')."
        },
        "response_mode": {
            "type": "string",
            "enum": ["text", "widget"],
            "default": "text",
            "description": "Response mode: 'text' for formatted text, 'widget' for interactive UI."
        },
        "params": {
            "type": "object",
            "description": "Optional query parameters",
            "additionalProperties": True
        }
    },
    "required": ["query"],
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
            "enum": ["basketball", "baseball", "football"],
            "description": "Sport type to query."
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
        }
    },
    "required": ["game_id"],
    "additionalProperties": False,
}
