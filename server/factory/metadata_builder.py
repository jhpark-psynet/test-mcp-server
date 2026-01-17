"""OpenAI 위젯 메타데이터 빌더."""
from typing import Any, Dict

import mcp.types as types

from server.config import Config, CONFIG
from server.models import Widget, ToolDefinition


def widget_tool_meta(tool: ToolDefinition) -> Dict[str, Any]:
    """Generate metadata for OpenAI widget tools.

    Args:
        tool: Tool definition

    Returns:
        Metadata dictionary for widget tools
    """
    if not tool.has_widget:
        return {}

    return {
        "openai/outputTemplate": tool.widget.template_uri,
        "openai/toolInvocation/invoking": tool.invoking,
        "openai/toolInvocation/invoked": tool.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "openai/widgetDomain": f"https://{CONFIG.effective_widget_domain}",
        "openai/widgetCSP": CONFIG.widget_csp,
        "openai/widgetDescription": tool.description,
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

    HTML is loaded fresh from disk each time to support hot reload without server restart.

    Args:
        cfg: Server configuration
        widget: Widget instance

    Returns:
        EmbeddedResource with widget HTML
    """
    from server.services.asset_loader import load_widget_html

    # Load HTML fresh from disk (supports hot reload)
    html = load_widget_html(widget.identifier, str(cfg.assets_dir))

    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=cfg.mime_type,
            text=html,
            title=widget.title,
        ),
    )
