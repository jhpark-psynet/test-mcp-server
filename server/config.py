"""서버 구성 설정 (Pydantic Settings 기반)."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """서버 구성 설정 (환경 변수 자동 검증).

    환경 변수 또는 .env 파일에서 설정을 로드합니다.
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    # Application
    app_name: str = Field(
        default="test-mcp-server",
        description="Application name"
    )

    # Assets
    assets_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / "components" / "assets",
        description="Widget assets directory"
    )

    mime_type: str = Field(
        default="text/html+skybridge",
        description="Widget MIME type"
    )

    # HTTP Server
    http_host: str = Field(
        default="0.0.0.0",
        alias="HTTP_HOST",
        description="Server host"
    )

    http_port: int = Field(
        default=8000,
        alias="HTTP_PORT",
        ge=1,
        le=65535,
        description="Server port"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Component server (for fetching widget manifest)
    component_base_url: str = Field(
        default="http://localhost:4444",
        alias="COMPONENT_BASE_URL",
        description="Component server base URL for fetching widget hashes (e.g., http://localhost:4444 or CDN URL)"
    )

    # CORS
    cors_allow_origins: Tuple[str, ...] = Field(
        default=("*",),
        description="CORS allowed origins"
    )

    cors_allow_methods: Tuple[str, ...] = Field(
        default=("*",),
        description="CORS allowed methods"
    )

    cors_allow_headers: Tuple[str, ...] = Field(
        default=("*",),
        description="CORS allowed headers"
    )

    cors_allow_credentials: bool = Field(
        default=False,
        description="CORS allow credentials"
    )

    # External API
    external_api_base_url: str = Field(
        default="",
        alias="EXTERNAL_API_BASE_URL",
        description="External API base URL (e.g., https://api.example.com)"
    )

    external_api_key: str = Field(
        default="",
        alias="EXTERNAL_API_KEY",
        description="External API authentication key"
    )

    external_api_timeout_s: float = Field(
        default=10.0,
        alias="EXTERNAL_API_TIMEOUT_S",
        gt=0,
        le=300,
        description="API request timeout in seconds"
    )

    external_api_auth_header: str = Field(
        default="Authorization",
        alias="EXTERNAL_API_AUTH_HEADER",
        description="HTTP header name for authentication"
    )

    external_api_auth_scheme: str = Field(
        default="Bearer",
        alias="EXTERNAL_API_AUTH_SCHEME",
        description="Authentication scheme (e.g., Bearer, Token, ApiKey)"
    )

    # Validators
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of {valid_levels}"
            )
        return v_upper

    @field_validator('external_api_base_url')
    @classmethod
    def validate_api_url(cls, v: str) -> str:
        """Validate external API URL format."""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError(
                f"External API URL must start with http:// or https://. Got: {v}"
            )
        # Remove trailing slashes
        return v.rstrip('/')

    @field_validator('assets_dir')
    @classmethod
    def validate_assets_dir(cls, v: Path) -> Path:
        """Validate assets directory exists."""
        if not v.exists():
            raise ValueError(
                f"Assets directory not found: {v}\n"
                f"Run 'npm run build' to generate widget assets."
            )
        if not v.is_dir():
            raise ValueError(f"Assets path is not a directory: {v}")
        return v

    # Computed properties
    @computed_field
    @property
    def has_external_api(self) -> bool:
        """Check if external API is configured."""
        return bool(self.external_api_base_url and self.external_api_key)

    # Compatibility properties (for backwards compatibility)
    @property
    def host(self) -> str:
        """Alias for http_host (backwards compatibility)."""
        return self.http_host

    @property
    def port(self) -> int:
        """Alias for http_port (backwards compatibility)."""
        return self.http_port


# Global config instance
try:
    CONFIG = Config()
except Exception as e:
    print(f"❌ Configuration error: {e}")
    print("\nPlease check your environment variables or .env file.")
    print("See .env.example for reference.")
    raise
