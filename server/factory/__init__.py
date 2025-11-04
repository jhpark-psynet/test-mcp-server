"""MCP server factory export."""
from server.factory.server_factory import create_mcp_server, create_app
from server.factory.metadata_builder import (
    widget_tool_meta,
    text_tool_meta,
    embedded_widget_resource,
)

__all__ = [
    "create_mcp_server",
    "create_app",
    "widget_tool_meta",
    "text_tool_meta",
    "embedded_widget_resource",
]
