"""MCP server with React widget support using FastMCP and OpenAI Apps SDK.

Refactored to separate concerns:
- Widget: Pure UI component definition
- ToolDefinition: MCP tool configuration (can be widget-based or text-based)
- Clear separation between UI rendering and tool execution logic
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Config:
    """런타임/빌드 구성값 모음."""
    app_name: str = "test-mcp-server"
    assets_dir: Path = Path(__file__).resolve().parent.parent / "components" / "assets"
    mime_type: str = "text/html+skybridge"

    # HTTP
    host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    port: int = int(os.getenv("HTTP_PORT", "8000"))

    # CORS
    cors_allow_origins: tuple[str, ...] = ("*",)
    cors_allow_methods: tuple[str, ...] = ("*",)
    cors_allow_headers: tuple[str, ...] = ("*",)
    cors_allow_credentials: bool = False


CONFIG = Config()


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logger = logging.getLogger("mcp-server")
if not logger.handlers:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


# -----------------------------------------------------------------------------
# Domain models / Schemas
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Widget:
    """Pure UI component definition (no tool-specific metadata)."""
    identifier: str
    title: str
    template_uri: str
    html: str


class ToolType(str, Enum):
    """Tool response type."""
    TEXT = "text"
    WIDGET = "widget"


@dataclass(frozen=True)
class ToolDefinition:
    """MCP Tool definition supporting both text-based and widget-based tools."""
    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    tool_type: ToolType

    # Optional: Widget reference (only for widget-based tools)
    widget: Optional[Widget] = None

    # Tool invocation metadata
    invoking: str = "Processing..."
    invoked: str = "Completed"

    # Text response (only for text-based tools)
    handler: Optional[Callable[[Dict[str, Any]], str]] = None

    @property
    def is_widget_tool(self) -> bool:
        """Check if this tool returns a widget."""
        return self.tool_type == ToolType.WIDGET and self.widget is not None

    @property
    def is_text_tool(self) -> bool:
        """Check if this tool returns text only."""
        return self.tool_type == ToolType.TEXT and self.handler is not None


# Input schemas
class WidgetToolInput(BaseModel):
    """Schema for widget tool input."""
    message: str = Field(..., description="Message to pass to the widget.")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class CalculatorToolInput(BaseModel):
    """Schema for calculator tool input."""
    expression: str = Field(..., description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5').")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


# JSON schemas for tools
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

CALCULATOR_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "expression": {
            "type": "string",
            "description": "Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5').",
        }
    },
    "required": ["expression"],
    "additionalProperties": False,
}


# -----------------------------------------------------------------------------
# Assets loading
# -----------------------------------------------------------------------------

@lru_cache(maxsize=None)
def load_widget_html(component_name: str, assets_dir_str: str) -> str:
    """Load widget HTML from assets directory (with hashed-filename fallback)."""
    assets_dir = Path(assets_dir_str)
    if not assets_dir.exists():
        raise FileNotFoundError(
            f"Assets directory not found: {assets_dir}. "
            "Run `npm run build` to generate the assets before starting the server."
        )

    html_path = assets_dir / f"{component_name}.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf8")

    # Try with hash suffix (e.g., my-app-a1b2.html)
    fallback_candidates = sorted(assets_dir.glob(f"{component_name}-*.html"))
    if fallback_candidates:
        return fallback_candidates[-1].read_text(encoding="utf8")

    raise FileNotFoundError(
        f'Widget HTML for "{component_name}" not found in {assets_dir}. '
        "Run `npm run build` to generate the assets before starting the server."
    )


# -----------------------------------------------------------------------------
# Tool handlers (business logic)
# -----------------------------------------------------------------------------

def calculator_handler(arguments: Dict[str, Any]) -> str:
    """Handle calculator tool execution."""
    expression = arguments.get("expression", "")
    try:
        # Safe evaluation (limited to basic math operations)
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


# -----------------------------------------------------------------------------
# Widget and Tool registry
# -----------------------------------------------------------------------------

def build_widgets(cfg: Config) -> list[Widget]:
    """Build list of available widgets."""
    example_html = load_widget_html("example", str(cfg.assets_dir))
    return [
        Widget(
            identifier="example-widget",
            title="Example Widget",
            template_uri="ui://widget/example.html",
            html=example_html,
        )
    ]


def build_tools(cfg: Config) -> list[ToolDefinition]:
    """Build list of available tools (both widget-based and text-based)."""
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

    return tools


def index_tools(tools: list[ToolDefinition]) -> dict[str, ToolDefinition]:
    """Create tool index by name."""
    return {t.name: t for t in tools}


def index_widgets_by_uri(tools: list[ToolDefinition]) -> dict[str, Widget]:
    """Create widget index by URI (for resource reads)."""
    result = {}
    for tool in tools:
        if tool.is_widget_tool and tool.widget:
            result[tool.widget.template_uri] = tool.widget
    return result


# -----------------------------------------------------------------------------
# OpenAI widget metadata helpers
# -----------------------------------------------------------------------------

def widget_tool_meta(tool: ToolDefinition) -> Dict[str, Any]:
    """Generate metadata for OpenAI widget tools."""
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
    """Generate metadata for text-based tools."""
    return {
        "openai/toolInvocation/invoking": tool.invoking,
        "openai/toolInvocation/invoked": tool.invoked,
    }


def embedded_widget_resource(cfg: Config, widget: Widget) -> types.EmbeddedResource:
    """Create an embedded widget resource containing the HTML."""
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=cfg.mime_type,
            text=widget.html,
            title=widget.title,
        ),
    )


# -----------------------------------------------------------------------------
# MCP server and handlers
# -----------------------------------------------------------------------------

def create_mcp_server(cfg: Config) -> FastMCP:
    """FastMCP 서버를 생성하고 핸들러를 등록."""
    mcp = FastMCP(
        name=cfg.app_name,
        stateless_http=True,
    )

    tools = build_tools(cfg)
    tools_by_name = index_tools(tools)
    widgets_by_uri = index_widgets_by_uri(tools)

    @mcp._mcp_server.list_tools()
    async def _list_tools() -> List[types.Tool]:
        result = []
        for tool in tools:
            tool_meta = widget_tool_meta(tool) if tool.is_widget_tool else text_tool_meta(tool)
            result.append(
                types.Tool(
                    name=tool.name,
                    title=tool.title,
                    description=tool.description,
                    inputSchema=tool.input_schema,
                    _meta=tool_meta,
                    annotations={
                        "destructiveHint": False,
                        "openWorldHint": False,
                        "readOnlyHint": True,
                    },
                )
            )
        return result

    @mcp._mcp_server.list_resources()
    async def _list_resources() -> List[types.Resource]:
        """List only widget resources (text tools don't have resources)."""
        result = []
        for tool in tools:
            if tool.is_widget_tool and tool.widget:
                result.append(
                    types.Resource(
                        name=tool.widget.title,
                        title=tool.widget.title,
                        uri=tool.widget.template_uri,
                        description=f"{tool.widget.title} widget markup",
                        mimeType=cfg.mime_type,
                        _meta=widget_tool_meta(tool),
                    )
                )
        return result

    @mcp._mcp_server.list_resource_templates()
    async def _list_resource_templates() -> List[types.ResourceTemplate]:
        """List only widget resource templates."""
        result = []
        for tool in tools:
            if tool.is_widget_tool and tool.widget:
                result.append(
                    types.ResourceTemplate(
                        name=tool.widget.title,
                        title=tool.widget.title,
                        uriTemplate=tool.widget.template_uri,
                        description=f"{tool.widget.title} widget markup",
                        mimeType=cfg.mime_type,
                        _meta=widget_tool_meta(tool),
                    )
                )
        return result

    async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
        """Handle resource read requests (only for widgets)."""
        widget = widgets_by_uri.get(str(req.params.uri))
        if widget is None:
            logger.warning("Unknown resource read: %s", req.params.uri)
            return types.ServerResult(
                types.ReadResourceResult(
                    contents=[],
                    _meta={"error": f"Unknown resource: {req.params.uri}"},
                )
            )

        # Find the tool that owns this widget for metadata
        tool_meta = {}
        for tool in tools:
            if tool.is_widget_tool and tool.widget == widget:
                tool_meta = widget_tool_meta(tool)
                break

        contents = [
            types.TextResourceContents(
                uri=widget.template_uri,
                mimeType=cfg.mime_type,
                text=widget.html,
                _meta=tool_meta,
            )
        ]
        return types.ServerResult(types.ReadResourceResult(contents=contents))

    async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
        """Handle tool call requests (both widget and text tools)."""
        tool = tools_by_name.get(req.params.name)
        if tool is None:
            logger.warning("Unknown tool call: %s", req.params.name)
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Unknown tool: {req.params.name}",
                        )
                    ],
                    isError=True,
                )
            )

        arguments = req.params.arguments or {}

        # Widget-based tool
        if tool.is_widget_tool and tool.widget:
            try:
                payload = WidgetToolInput.model_validate(arguments)
            except ValidationError as exc:
                logger.debug("Input validation error: %s", exc)
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=f"Input validation error: {exc.errors()}",
                            )
                        ],
                        isError=True,
                    )
                )

            message = payload.message
            widget_resource = embedded_widget_resource(cfg, tool.widget)

            meta: Dict[str, Any] = {
                "openai.com/widget": widget_resource.model_dump(mode="json"),
                **widget_tool_meta(tool),
            }

            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Rendered {tool.widget.title}",
                        )
                    ],
                    structuredContent={"message": message},
                    _meta=meta,
                )
            )

        # Text-based tool
        elif tool.is_text_tool and tool.handler:
            try:
                # Validate based on tool's schema
                if tool.name == "calculator":
                    payload = CalculatorToolInput.model_validate(arguments)
                    validated_args = payload.model_dump()
                else:
                    validated_args = arguments
            except ValidationError as exc:
                logger.debug("Input validation error: %s", exc)
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=f"Input validation error: {exc.errors()}",
                            )
                        ],
                        isError=True,
                    )
                )

            # Execute handler
            try:
                result_text = tool.handler(validated_args)
            except Exception as exc:
                logger.error("Tool execution error: %s", exc)
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=f"Execution error: {str(exc)}",
                            )
                        ],
                        isError=True,
                    )
                )

            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=result_text,
                        )
                    ],
                    _meta=text_tool_meta(tool),
                )
            )

        else:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Tool {tool.name} is not properly configured",
                        )
                    ],
                    isError=True,
                )
            )

    # Register request handlers
    mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
    mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource

    return mcp


# -----------------------------------------------------------------------------
# App factory (Starlette app over SSE/HTTP)
# -----------------------------------------------------------------------------

def create_app(cfg: Config):
    mcp = create_mcp_server(cfg)
    app = mcp.streamable_http_app()

    # Add CORS middleware if available (optional dependency)
    try:
        from starlette.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(cfg.cors_allow_origins),
            allow_methods=list(cfg.cors_allow_methods),
            allow_headers=list(cfg.cors_allow_headers),
            allow_credentials=cfg.cors_allow_credentials,
        )
    except Exception:  # starlette 미설치 등 환경 대응
        logger.debug("CORS middleware not applied (starlette missing or import error).")

    return app


# Module-level ASGI app (uvicorn entrypoint friendly)
app = create_app(CONFIG)


if __name__ == "__main__":
    import uvicorn

    print(f"Starting MCP server on http://{CONFIG.host}:{CONFIG.port}")
    print(f"Assets directory: {CONFIG.assets_dir}")
    uvicorn.run("main:app", host=CONFIG.host, port=CONFIG.port, reload=True)
