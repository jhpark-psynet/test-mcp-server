"""MCP server with React widget support using FastMCP and OpenAI Apps SDK.

- 구성 책임 분리: 설정, 위젯 로딩, 서버/앱 생성, 요청 핸들러
- 테스트 용이성: 팩토리 함수들(create_mcp_server, create_app)로 의존성 주입 쉬움
- 일관된 메타데이터 생성, 엄격한 입력 검증, 명확한 로깅
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

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
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: str


class ToolInput(BaseModel):
    """Schema for tool input."""
    message: str = Field(..., description="Message to pass to the widget.")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


# OpenAI widget tool input schema (JSON Schema)
TOOL_INPUT_SCHEMA: Dict[str, Any] = {
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
# Widget registry
# -----------------------------------------------------------------------------

def build_widgets(cfg: Config) -> list[Widget]:
    """등록할 위젯 목록을 구성."""
    example_html = load_widget_html("example", str(cfg.assets_dir))
    return [
        Widget(
            identifier="example-widget",
            title="Example Widget",
            template_uri="ui://widget/example.html",
            invoking="Loading example widget",
            invoked="Example widget loaded",
            html=example_html,
            response_text="Rendered example widget!",
        )
    ]


def index_widgets(widgets: list[Widget]) -> tuple[dict[str, Widget], dict[str, Widget]]:
    """ID/URI 인덱스 생성."""
    by_id = {w.identifier: w for w in widgets}
    by_uri = {w.template_uri: w for w in widgets}
    return by_id, by_uri


# -----------------------------------------------------------------------------
# OpenAI widget metadata helpers
# -----------------------------------------------------------------------------

def resource_description(widget: Widget) -> str:
    return f"{widget.title} widget markup"


def tool_meta(widget: Widget) -> Dict[str, Any]:
    """Generate metadata for OpenAI widget tools."""
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
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

    widgets = build_widgets(cfg)
    widgets_by_id, widgets_by_uri = index_widgets(widgets)

    @mcp._mcp_server.list_tools()
    async def _list_tools() -> List[types.Tool]:
        return [
            types.Tool(
                name=w.identifier,
                title=w.title,
                description=w.title,
                inputSchema=TOOL_INPUT_SCHEMA,
                _meta=tool_meta(w),
                annotations={
                    "destructiveHint": False,
                    "openWorldHint": False,
                    "readOnlyHint": True,
                },
            )
            for w in widgets
        ]

    @mcp._mcp_server.list_resources()
    async def _list_resources() -> List[types.Resource]:
        return [
            types.Resource(
                name=w.title,
                title=w.title,
                uri=w.template_uri,
                description=resource_description(w),
                mimeType=cfg.mime_type,
                _meta=tool_meta(w),
            )
            for w in widgets
        ]

    @mcp._mcp_server.list_resource_templates()
    async def _list_resource_templates() -> List[types.ResourceTemplate]:
        return [
            types.ResourceTemplate(
                name=w.title,
                title=w.title,
                uriTemplate=w.template_uri,
                description=resource_description(w),
                mimeType=cfg.mime_type,
                _meta=tool_meta(w),
            )
            for w in widgets
        ]

    async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
        """Handle resource read requests."""
        widget = widgets_by_uri.get(str(req.params.uri))
        if widget is None:
            logger.warning("Unknown resource read: %s", req.params.uri)
            return types.ServerResult(
                types.ReadResourceResult(
                    contents=[],
                    _meta={"error": f"Unknown resource: {req.params.uri}"},
                )
            )

        contents = [
            types.TextResourceContents(
                uri=widget.template_uri,
                mimeType=cfg.mime_type,
                text=widget.html,
                _meta=tool_meta(widget),
            )
        ]
        return types.ServerResult(types.ReadResourceResult(contents=contents))

    async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
        """Handle tool call requests."""
        widget = widgets_by_id.get(req.params.name)
        if widget is None:
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
        try:
            payload = ToolInput.model_validate(arguments)
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
        widget_resource = embedded_widget_resource(cfg, widget)

        meta: Dict[str, Any] = {
            "openai.com/widget": widget_resource.model_dump(mode="json"),
            "openai/outputTemplate": widget.template_uri,
            "openai/toolInvocation/invoking": widget.invoking,
            "openai/toolInvocation/invoked": widget.invoked,
            "openai/widgetAccessible": True,
            "openai/resultCanProduceWidget": True,
        }

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=widget.response_text,
                    )
                ],
                structuredContent={"message": message},
                _meta=meta,
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
