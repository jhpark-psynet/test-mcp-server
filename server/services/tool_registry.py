"""툴 레지스트리."""
import logging
from typing import Dict, List

from server.config import Config
from server.models import (
    ToolDefinition,
    ToolType,
    Widget,
    WIDGET_TOOL_INPUT_SCHEMA,
    CALCULATOR_TOOL_INPUT_SCHEMA,
    EXTERNAL_TOOL_INPUT_SCHEMA,
)
from server.services.widget_registry import build_widgets

logger = logging.getLogger(__name__)


def build_tools(cfg: Config, calculator_handler=None) -> List[ToolDefinition]:
    """Build list of available tools (both widget-based and text-based).

    Args:
        cfg: Server configuration
        calculator_handler: Calculator tool handler function

    Returns:
        List of ToolDefinition instances
    """
    widgets = build_widgets(cfg)
    tools = []

    # Widget-based tools
    for widget in widgets:
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

    # Text-based tools
    tools.append(
        ToolDefinition(
            name="calculator",
            title="Calculator",
            description="Evaluate mathematical expressions (e.g., '2 + 2', '10 * 5')",
            input_schema=CALCULATOR_TOOL_INPUT_SCHEMA,
            tool_type=ToolType.TEXT,
            handler=calculator_handler,
            invoking="Calculating...",
            invoked="Calculation complete",
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
