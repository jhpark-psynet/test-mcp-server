"""Tool 도메인 모델."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from server.models.widget import Widget


@dataclass(frozen=True)
class ToolDefinition:
    """MCP 툴 정의."""
    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    widget: Optional[Widget] = None
    handler: Optional[Callable[[Dict[str, Any]], Any]] = None
    invoking: str = "Processing..."
    invoked: str = "Completed"

    @property
    def has_widget(self) -> bool:
        """Check if this tool produces widget output."""
        return self.widget is not None
