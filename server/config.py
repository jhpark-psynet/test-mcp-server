"""서버 구성 설정."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """런타임/빌드 구성값 모음."""
    app_name: str = "test-mcp-server"
    assets_dir: Path = Path(__file__).resolve().parent.parent / "components" / "assets"
    mime_type: str = "text/html+skybridge"

    # HTTP
    host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    port: int = int(os.getenv("HTTP_PORT", "8000"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS
    cors_allow_origins: tuple[str, ...] = ("*",)
    cors_allow_methods: tuple[str, ...] = ("*",)
    cors_allow_headers: tuple[str, ...] = ("*",)
    cors_allow_credentials: bool = False

    # External API
    external_api_base_url: str = os.getenv("EXTERNAL_API_BASE_URL", "")
    external_api_key: str = os.getenv("EXTERNAL_API_KEY", "")
    external_api_timeout_s: float = float(os.getenv("EXTERNAL_API_TIMEOUT_S", "10.0"))
    external_api_auth_header: str = os.getenv("EXTERNAL_API_AUTH_HEADER", "Authorization")
    external_api_auth_scheme: str = os.getenv("EXTERNAL_API_AUTH_SCHEME", "Bearer")

    @property
    def has_external_api(self) -> bool:
        """Check if external API is configured."""
        return bool(self.external_api_base_url and self.external_api_key)


# Global config instance
CONFIG = Config()
