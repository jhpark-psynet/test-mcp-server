"""Tool 도메인 모델."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from server.models.widget import Widget, ToolType


@dataclass(frozen=True)
class ToolDefinition:
    """MCP 툴 정의 (위젯 또는 텍스트 기반)."""
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
        """Check if this is a widget-based tool."""
        return self.tool_type == ToolType.WIDGET and self.widget is not None

    @property
    def is_text_tool(self) -> bool:
        """Check if this is a text-based tool."""
        return self.tool_type == ToolType.TEXT and self.handler is not None
