"""툴 레지스트리."""
import logging
from typing import Dict, List

from server.config import Config
from server.models import (
    ToolDefinition,
    ToolType,
    Widget,
    WIDGET_TOOL_INPUT_SCHEMA,
    EXTERNAL_TOOL_INPUT_SCHEMA,
    GET_GAMES_BY_SPORT_SCHEMA,
    GET_GAME_DETAILS_SCHEMA,
)
from server.services.widget_registry import build_widgets

logger = logging.getLogger(__name__)


def build_tools(
    cfg: Config,
    get_games_by_sport_handler=None,
    get_game_details_handler=None,
) -> List[ToolDefinition]:
    """Build list of available tools (both widget-based and text-based).

    Args:
        cfg: Server configuration
        get_games_by_sport_handler: Sports game list handler function
        get_game_details_handler: Game details (widget) handler function

    Returns:
        List of ToolDefinition instances
    """
    widgets = build_widgets(cfg)
    tools = []

    # Find game-result-viewer widget for get_game_details
    game_result_viewer_widget = None
    for widget in widgets:
        if widget.identifier == "game-result-viewer":
            game_result_viewer_widget = widget
            break

    # Widget-based tools (standard widgets with message input)
    for widget in widgets:
        # Skip widgets that are used internally or for testing only
        if widget.identifier in ["game-stats-widget", "game-result-viewer", "example-widget"]:
            continue

        tools.append(
            ToolDefinition(
                name=widget.identifier,
                title=widget.title,
                description=f"Display {widget.title} interactive component",
                input_schema=WIDGET_TOOL_INPUT_SCHEMA,
                tool_type=ToolType.WIDGET,
                widget=widget,
                invoking=f"Loading {widget.title}...",
                invoked=f"{widget.title} loaded",
            )
        )

    # External API tool (only if configured)
    if cfg.has_external_api:
        tools.append(
            ToolDefinition(
                name="external-fetch",
                title="External API Fetch",
                description=(
                    "Fetch data from external API with dual response modes. "
                    "Use 'text' mode for formatted output or 'widget' mode for interactive UI."
                ),
                input_schema=EXTERNAL_TOOL_INPUT_SCHEMA,
                tool_type=ToolType.TEXT,  # Can return both text and widget based on response_mode
                handler=None,  # Handled directly in _call_tool_request
                invoking="Fetching from external API...",
                invoked="API fetch complete",
            )
        )
        logger.info("External API tool registered: %s", cfg.external_api_base_url)
    else:
        logger.debug("External API not configured, skipping external-fetch tool")

    # Sports data tools
    if get_games_by_sport_handler:
        tools.append(
            ToolDefinition(
                name="get_games_by_sport",
                title="Get Games by Sport",
                description=(
                    "Retrieve sports game schedules and results for a specific date and sport. "
                    "Returns game information including teams, scores, time, arena, and game state. "
                    "Team filtering can be done by searching home_team_name or away_team_name in results. "
                    "\n\nSupported sports: basketball, baseball, football"
                    "\n\nCommon team aliases:"
                    "\n- Warriors, Goldens → Golden State (NBA)"
                    "\n- Cavs → Cleveland (NBA)"
                    "\n- Thunder → Oklahoma City (NBA)"
                    "\n- Bluemings → Yongin Samsung Life (WKBL)"
                    "\n- S-Birds → Incheon Shinhan Bank (WKBL)"
                ),
                input_schema=GET_GAMES_BY_SPORT_SCHEMA,
                tool_type=ToolType.TEXT,
                handler=get_games_by_sport_handler,
                invoking="Fetching game schedules...",
                invoked="Game schedules retrieved",
            )
        )

    # get_game_details: Widget-based tool with custom handler
    if get_game_details_handler and game_result_viewer_widget:
        tools.append(
            ToolDefinition(
                name="get_game_details",
                title="Game Details",
                description=(
                    "Retrieve detailed game statistics including team and player stats with interactive visualization. "
                    "Returns game information, team statistics (field goals, rebounds, assists, etc.), "
                    "and player statistics (points, rebounds, assists, shooting percentages, etc.) in a widget. "
                    "\n\nNote: Only available for finished games (state='f'). "
                    "Use get_games_by_sport first to get the game_id."
                ),
                input_schema=GET_GAME_DETAILS_SCHEMA,
                tool_type=ToolType.WIDGET,
                widget=game_result_viewer_widget,
                handler=get_game_details_handler,
                invoking="Loading game details...",
                invoked="Game details loaded",
            )
        )

    return tools


def index_tools(tools: List[ToolDefinition]) -> Dict[str, ToolDefinition]:
    """Create tool index by name.

    Args:
        tools: List of tools

    Returns:
        Dictionary mapping tool name to ToolDefinition
    """
    return {t.name: t for t in tools}


def index_widgets_by_uri(tools: List[ToolDefinition]) -> Dict[str, Widget]:
    """Create widget index by URI (for resource reads).

    Args:
        tools: List of tools

    Returns:
        Dictionary mapping widget URI to Widget
    """
    result = {}
    for tool in tools:
        if tool.is_widget_tool and tool.widget:
            result[tool.widget.template_uri] = tool.widget
    return result
