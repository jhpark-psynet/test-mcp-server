"""FastMCP 비공개 API를 안전하게 래핑."""
import logging
from typing import Callable

import mcp.types as types
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


class FastMCPInternalAPIError(RuntimeError):
    """FastMCP 내부 API 변경으로 인한 에러."""
    pass


class SafeFastMCPWrapper:
    """FastMCP 비공개 API 접근을 안전하게 래핑.

    FastMCP 내부 구조 변경을 감지하고 명확한 에러 메시지를 제공합니다.
    """

    def __init__(self, mcp: FastMCP):
        """Initialize wrapper.

        Args:
            mcp: FastMCP instance to wrap

        Raises:
            FastMCPInternalAPIError: If FastMCP internal structure is incompatible
        """
        self._mcp = mcp
        self._validate_internal_api()

    def _validate_internal_api(self) -> None:
        """FastMCP 내부 구조 검증.

        Raises:
            FastMCPInternalAPIError: If required attributes are missing
        """
        if not hasattr(self._mcp, '_mcp_server'):
            raise FastMCPInternalAPIError(
                "FastMCP internal structure changed: '_mcp_server' attribute not found. "
                "This may be due to a FastMCP version update. "
                "Please check the FastMCP changelog and update the wrapper."
            )

        if not hasattr(self._mcp._mcp_server, 'request_handlers'):
            raise FastMCPInternalAPIError(
                "FastMCP internal structure changed: 'request_handlers' attribute not found. "
                "This may be due to a FastMCP version update."
            )

        logger.debug("FastMCP internal API validation passed")

    def list_tools_decorator(self) -> Callable:
        """Get list_tools decorator safely.

        Returns:
            list_tools decorator function

        Raises:
            FastMCPInternalAPIError: If decorator is not available
        """
        try:
            return self._mcp._mcp_server.list_tools
        except AttributeError as e:
            raise FastMCPInternalAPIError(
                f"FastMCP 'list_tools' decorator not found: {e}. "
                "The FastMCP API may have changed."
            ) from e

    def list_resources_decorator(self) -> Callable:
        """Get list_resources decorator safely.

        Returns:
            list_resources decorator function

        Raises:
            FastMCPInternalAPIError: If decorator is not available
        """
        try:
            return self._mcp._mcp_server.list_resources
        except AttributeError as e:
            raise FastMCPInternalAPIError(
                f"FastMCP 'list_resources' decorator not found: {e}"
            ) from e

    def list_resource_templates_decorator(self) -> Callable:
        """Get list_resource_templates decorator safely.

        Returns:
            list_resource_templates decorator function

        Raises:
            FastMCPInternalAPIError: If decorator is not available
        """
        try:
            return self._mcp._mcp_server.list_resource_templates
        except AttributeError as e:
            raise FastMCPInternalAPIError(
                f"FastMCP 'list_resource_templates' decorator not found: {e}"
            ) from e

    def register_request_handler(
        self,
        request_type: type,
        handler: Callable
    ) -> None:
        """Register a request handler safely.

        Args:
            request_type: MCP request type (e.g., types.CallToolRequest)
            handler: Handler function

        Raises:
            FastMCPInternalAPIError: If registration fails
        """
        try:
            self._mcp._mcp_server.request_handlers[request_type] = handler
            logger.debug(f"Registered handler for {request_type.__name__}")
        except (AttributeError, KeyError, TypeError) as e:
            raise FastMCPInternalAPIError(
                f"Failed to register handler for {request_type.__name__}: {e}. "
                "The FastMCP request handler registration API may have changed."
            ) from e

    def get_underlying_mcp(self) -> FastMCP:
        """Get the underlying FastMCP instance.

        Use with caution - prefer using wrapper methods.

        Returns:
            FastMCP instance
        """
        return self._mcp
