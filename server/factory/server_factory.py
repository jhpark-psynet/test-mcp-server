"""MCP 서버 팩토리."""
from __future__ import annotations

import inspect
import logging
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from server.errors import APIError, format_validation_errors

from server.config import Config
from server.models import (
    WidgetToolInput,
    GetGamesBySportInput,
    GetGameDetailsInput,
)
from server.services import (
    build_tools,
    index_tools,
    index_widgets_by_uri,
)
from server.handlers import (
    get_games_by_sport_handler,
    get_game_details_handler,
)
from server.factory.metadata_builder import (
    widget_tool_meta,
    text_tool_meta,
    embedded_widget_resource,
)
from server.factory.safe_wrapper import SafeFastMCPWrapper

logger = logging.getLogger(__name__)


def create_mcp_server(cfg: Config) -> FastMCP:
    """FastMCP 서버를 생성하고 핸들러를 등록 (SafeFastMCPWrapper 사용).

    Args:
        cfg: Server configuration

    Returns:
        Configured FastMCP server instance

    Raises:
        FastMCPInternalAPIError: If FastMCP internal API is incompatible
    """
    mcp = FastMCP(
        name=cfg.app_name,
        stateless_http=True,
    )

    # Wrap FastMCP with safety layer
    wrapper = SafeFastMCPWrapper(mcp)

    # Build tools and create indices
    tools = build_tools(
        cfg,
        get_games_by_sport_handler=get_games_by_sport_handler,
        get_game_details_handler=get_game_details_handler,
    )
    tools_by_name = index_tools(tools)
    widgets_by_uri = index_widgets_by_uri(tools)

    logger.info(f"Registered {len(tools)} tools")

    @wrapper.list_tools_decorator()()
    async def _list_tools() -> List[types.Tool]:
        """List all available MCP tools."""
        result = []
        for tool in tools:
            tool_meta = widget_tool_meta(tool) if tool.has_widget else text_tool_meta(tool)
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

    @wrapper.list_resources_decorator()()
    async def _list_resources() -> List[types.Resource]:
        """List only widget resources (text tools don't have resources)."""
        result = []
        for tool in tools:
            if tool.has_widget:
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

    @wrapper.list_resource_templates_decorator()()
    async def _list_resource_templates() -> List[types.ResourceTemplate]:
        """List only widget resource templates."""
        result = []
        for tool in tools:
            if tool.has_widget:
                result.append(
                    types.ResourceTemplate(
                        name=tool.widget.title,
                        uriTemplate=tool.widget.template_uri,
                        description=f"{tool.widget.title} widget template",
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
            if tool.has_widget and tool.widget == widget:
                tool_meta = widget_tool_meta(tool)
                break

        # Load HTML fresh from disk (supports hot reload)
        from server.services.asset_loader import load_widget_html
        html = load_widget_html(widget.identifier, str(cfg.assets_dir))

        contents = [
            types.TextResourceContents(
                uri=widget.template_uri,
                mimeType=cfg.mime_type,
                text=html,
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

        # Validate input using tool's schema
        try:
            # Use Pydantic model based on tool name
            if tool.name == "get_games_by_sport":
                payload = GetGamesBySportInput.model_validate(arguments)
            elif tool.name == "get_game_details":
                payload = GetGameDetailsInput.model_validate(arguments)
            elif tool.has_widget:
                payload = WidgetToolInput.model_validate(arguments)
            else:
                # No validation for unknown tools
                payload = None

            validated_args = payload.model_dump() if payload else arguments
        except ValidationError as exc:
            logger.debug("Input validation error: %s", exc)
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=format_validation_errors(exc.errors()),
                        )
                    ],
                    isError=True,
                )
            )

        # Widget-based tool
        if tool.has_widget:
            # get_game_details: has custom handler
            if tool.name == "get_game_details" and tool.handler:
                # Execute handler to get structured data
                try:
                    # Support both sync and async handlers
                    if inspect.iscoroutinefunction(tool.handler):
                        structured_data = await tool.handler(validated_args)
                    else:
                        structured_data = tool.handler(validated_args)
                except APIError as exc:
                    logger.error("API error [%s]: %s", exc.code.value, exc.detail)
                    return types.ServerResult(
                        types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text=exc.user_message,
                                )
                            ],
                            isError=True,
                        )
                    )
                except Exception as exc:
                    logger.error("Tool execution error: %s", exc)
                    return types.ServerResult(
                        types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text="An unexpected error occurred. Please try again later.",
                                )
                            ],
                            isError=True,
                        )
                    )

                # Create widget resource
                widget_resource = embedded_widget_resource(cfg, tool.widget)

                # Widget metadata
                logger.info(f"[get_game_details] Sending metadata with template_uri: {tool.widget.template_uri}")
                logger.info(f"[get_game_details] Widget identifier: {tool.widget.identifier}")
                widget_meta: Dict[str, Any] = {
                    "openai.com/widget": widget_resource.model_dump(mode="json"),
                    "openai/outputTemplate": tool.widget.template_uri,
                    "openai/toolInvocation/invoking": tool.invoking,
                    "openai/toolInvocation/invoked": tool.invoked,
                    "openai/widgetAccessible": True,
                    "openai/resultCanProduceWidget": True,
                }

                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=f"Game details loaded for {validated_args['game_id']}",
                            )
                        ],
                        structuredContent=structured_data,
                        _meta=widget_meta,
                    )
                )

            # Standard widget tools (example-widget, api-result-widget)
            else:
                message = validated_args.get("message", "")
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

        # Text-based tool (has handler but no widget)
        elif tool.handler:
            try:
                # Validate based on tool's schema
                if tool.name == "get_games_by_sport":
                    payload = GetGamesBySportInput.model_validate(arguments)
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
                                text=format_validation_errors(exc.errors()),
                            )
                        ],
                        isError=True,
                    )
                )

            # Execute handler
            try:
                # Support both sync and async handlers
                if inspect.iscoroutinefunction(tool.handler):
                    result_text = await tool.handler(validated_args)
                else:
                    result_text = tool.handler(validated_args)
            except APIError as exc:
                logger.error("API error [%s]: %s", exc.code.value, exc.detail)
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=exc.user_message,
                            )
                        ],
                        isError=True,
                    )
                )
            except Exception as exc:
                logger.error("Tool execution error: %s", exc)
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="An unexpected error occurred. Please try again later.",
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

    # Register request handlers using safe wrapper
    wrapper.register_request_handler(types.CallToolRequest, _call_tool_request)
    wrapper.register_request_handler(types.ReadResourceRequest, _handle_read_resource)

    return mcp


def create_app(cfg: Config):
    """Create ASGI application with CORS support and static file serving.

    Args:
        cfg: Server configuration

    Returns:
        ASGI application instance
    """
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
        logger.debug("CORS middleware applied")
    except Exception as e:
        logger.debug(f"CORS middleware not applied: {e}")

    # Mount static files for widget assets
    try:
        from starlette.staticfiles import StaticFiles
        from starlette.routing import Mount

        if cfg.assets_dir.exists():
            # Add static file route at /assets
            app.routes.append(
                Mount("/assets", StaticFiles(directory=str(cfg.assets_dir)), name="assets")
            )
            logger.info(f"Static files mounted at /assets from {cfg.assets_dir}")
        else:
            logger.warning(f"Assets directory not found: {cfg.assets_dir}")
    except Exception as e:
        logger.warning(f"Static files not mounted: {e}")

    return app
