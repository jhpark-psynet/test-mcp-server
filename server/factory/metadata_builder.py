"""OpenAI 위젯 메타데이터 빌더."""
from typing import Any, Dict

import mcp.types as types

from server.config import Config
from server.models import Widget, ToolDefinition


def widget_tool_meta(tool: ToolDefinition) -> Dict[str, Any]:
    """Generate metadata for OpenAI widget tools.

    Args:
        tool: Tool definition

    Returns:
        Metadata dictionary for widget tools
    """
    if not tool.is_widget_tool or not tool.widget:
        return {}

    return {
        "openai/outputTemplate": tool.widget.template_uri,
        "openai/toolInvocation/invoking": tool.invoking,
        "openai/toolInvocation/invoked": tool.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }


def text_tool_meta(tool: ToolDefinition) -> Dict[str, Any]:
    """Generate metadata for text-based tools.

    Args:
        tool: Tool definition

    Returns:
        Metadata dictionary for text tools
    """
    return {
        "openai/toolInvocation/invoking": tool.invoking,
        "openai/toolInvocation/invoked": tool.invoked,
    }


def embedded_widget_resource(cfg: Config, widget: Widget) -> types.EmbeddedResource:
    """Create an embedded widget resource containing the HTML.

    Args:
        cfg: Server configuration
        widget: Widget instance

    Returns:
        EmbeddedResource with widget HTML
    """
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=cfg.mime_type,
            text=widget.html,
            title=widget.title,
        ),
    )
