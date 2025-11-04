"""MCP 서버 팩토리."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from server.config import Config
from server.models import (
    WidgetToolInput,
    CalculatorToolInput,
    ExternalToolInput,
)
from server.services import (
    build_tools,
    index_tools,
    index_widgets_by_uri,
    format_api_response_text,
    format_api_error_text,
    ExternalApiClient,
)
from server.services.exceptions import ApiTimeoutError, ApiHttpError, ApiConnectionError
from server.handlers import calculator_handler
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
    tools = build_tools(cfg, calculator_handler=calculator_handler)
    tools_by_name = index_tools(tools)
    widgets_by_uri = index_widgets_by_uri(tools)

    logger.info(f"Registered {len(tools)} tools")

    @wrapper.list_tools_decorator()()
    async def _list_tools() -> List[types.Tool]:
        """List all available MCP tools."""
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

    @wrapper.list_resources_decorator()()
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

    @wrapper.list_resource_templates_decorator()()
    async def _list_resource_templates() -> List[types.ResourceTemplate]:
        """List only widget resource templates."""
        result = []
        for tool in tools:
            if tool.is_widget_tool and tool.widget:
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

        # External API fetch tool (special handling)
        elif tool.name == "external-fetch":
            try:
                payload = ExternalToolInput.model_validate(arguments)
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

            query = payload.query
            response_mode = payload.response_mode
            params = payload.params

            # Create API client
            api_client = ExternalApiClient(
                base_url=cfg.external_api_base_url,
                api_key=cfg.external_api_key,
                timeout_seconds=cfg.external_api_timeout_s,
                auth_header=cfg.external_api_auth_header,
                auth_scheme=cfg.external_api_auth_scheme,
            )

            # Call external API
            try:
                data = await api_client.fetch_json(query, params=params)
                await api_client.close()

                # Text mode: Format as text
                if response_mode == "text":
                    result_text = format_api_response_text(data, query)
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

                # Widget mode: Return interactive UI
                else:  # response_mode == "widget"
                    # Find api-result widget
                    api_result_widget = None
                    for w in widgets_by_uri.values():
                        if w.identifier == "api-result-widget":
                            api_result_widget = w
                            break

                    if not api_result_widget:
                        return types.ServerResult(
                            types.CallToolResult(
                                content=[
                                    types.TextContent(
                                        type="text",
                                        text="API Result Widget not found. Build components first.",
                                    )
                                ],
                                isError=True,
                            )
                        )

                    # Create widget resource
                    widget_resource = embedded_widget_resource(cfg, api_result_widget)

                    # Prepare structured content for React component
                    structured_content = {
                        "success": True,
                        "endpoint": query,
                        "data": data,
                        "timestamp": datetime.now().isoformat(),
                    }

                    # Widget metadata
                    widget_meta: Dict[str, Any] = {
                        "openai.com/widget": widget_resource.model_dump(mode="json"),
                        "openai/outputTemplate": api_result_widget.template_uri,
                        "openai/toolInvocation/invoking": "Loading API result...",
                        "openai/toolInvocation/invoked": "API result loaded",
                        "openai/widgetAccessible": True,
                        "openai/resultCanProduceWidget": True,
                    }

                    return types.ServerResult(
                        types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text=f"Fetched data from {query}",
                                )
                            ],
                            structuredContent=structured_content,
                            _meta=widget_meta,
                        )
                    )

            except Exception as exc:
                await api_client.close()
                logger.error("External API error: %s", exc)

                # Text mode: Format error as text
                if response_mode == "text":
                    error_text = format_api_error_text(exc, query)
                    return types.ServerResult(
                        types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text=error_text,
                                )
                            ],
                            isError=True,
                        )
                    )

                # Widget mode: Show error in widget
                else:  # response_mode == "widget"
                    # Find api-result widget
                    api_result_widget = None
                    for w in widgets_by_uri.values():
                        if w.identifier == "api-result-widget":
                            api_result_widget = w
                            break

                    if not api_result_widget:
                        return types.ServerResult(
                            types.CallToolResult(
                                content=[
                                    types.TextContent(
                                        type="text",
                                        text=f"API Error: {str(exc)}",
                                    )
                                ],
                                isError=True,
                            )
                        )

                    # Determine error type and details
                    error_type = type(exc).__name__
                    error_message = str(exc)
                    error_details = None

                    if isinstance(exc, ApiTimeoutError):
                        error_details = f"Timeout: {exc.timeout_seconds}s"
                    elif isinstance(exc, ApiHttpError):
                        error_details = f"Status: {exc.status_code}\n{exc.response_text[:500]}"
                    elif isinstance(exc, ApiConnectionError):
                        error_details = "Could not connect to the API server"

                    # Create widget resource
                    widget_resource = embedded_widget_resource(cfg, api_result_widget)

                    # Prepare structured content for React component
                    structured_content = {
                        "success": False,
                        "endpoint": query,
                        "error": {
                            "type": error_type,
                            "message": error_message,
                            "details": error_details,
                        },
                        "timestamp": datetime.now().isoformat(),
                    }

                    # Widget metadata
                    widget_meta: Dict[str, Any] = {
                        "openai.com/widget": widget_resource.model_dump(mode="json"),
                        "openai/outputTemplate": api_result_widget.template_uri,
                        "openai/toolInvocation/invoking": "Loading API error...",
                        "openai/toolInvocation/invoked": "API error loaded",
                        "openai/widgetAccessible": True,
                        "openai/resultCanProduceWidget": True,
                    }

                    return types.ServerResult(
                        types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text=f"API request failed: {error_message}",
                                )
                            ],
                            structuredContent=structured_content,
                            _meta=widget_meta,
                            isError=True,
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
    """Create ASGI application with CORS support.

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

    return app
