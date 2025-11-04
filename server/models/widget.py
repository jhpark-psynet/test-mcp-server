"""Widget 도메인 모델."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ToolType(str, Enum):
    """Tool type enumeration."""
    WIDGET = "widget"
    TEXT = "text"


@dataclass(frozen=True)
class Widget:
    """위젯 정의 (순수 UI 컴포넌트)."""
    identifier: str
    title: str
    template_uri: str
    html: str
