"""Widget 도메인 모델."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Widget:
    """위젯 정의 (순수 UI 컴포넌트)."""
    identifier: str
    title: str
    template_uri: str
    # html 필드 제거: 매번 파일에서 읽도록 변경 (hot reload 지원)
