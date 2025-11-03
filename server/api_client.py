"""External API client with async support."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from exceptions import ApiTimeoutError, ApiHttpError, ApiConnectionError

logger = logging.getLogger("mcp-server.api-client")


class ExternalApiClient:
  """Async HTTP client for external API calls."""

  def __init__(
    self,
    base_url: str,
    api_key: str,
    timeout_seconds: float = 10.0,
    auth_header: str = "Authorization",
    auth_scheme: str = "Bearer",
  ):
    """Initialize API client.

    Args:
        base_url: Base URL of external API (e.g., "https://api.example.com")
        api_key: API key for authentication
        timeout_seconds: Request timeout in seconds
        auth_header: HTTP header name for auth (default: "Authorization")
        auth_scheme: Auth scheme prefix (default: "Bearer")
    """
    self.base_url = base_url.rstrip("/")
    self.api_key = api_key
    self.timeout_seconds = timeout_seconds
    self.auth_header = auth_header
    self.auth_scheme = auth_scheme

    # Create async client with timeout
    self.client = httpx.AsyncClient(
      base_url=self.base_url,
      timeout=httpx.Timeout(timeout_seconds),
      headers={
        self.auth_header: f"{self.auth_scheme} {self.api_key}"
      },
    )

    logger.info(
      "API client initialized: base_url=%s, timeout=%ss",
      self.base_url,
      self.timeout_seconds,
    )

  async def fetch_json(
    self,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    method: str = "GET",
  ) -> Dict[str, Any]:
    """Fetch JSON data from API endpoint.

    Args:
        endpoint: API endpoint path (e.g., "/users" or "/search")
        params: Query parameters or request body
        method: HTTP method (default: "GET")

    Returns:
        JSON response as dictionary

    Raises:
        ApiTimeoutError: Request timed out
        ApiHttpError: HTTP error (4xx, 5xx)
        ApiConnectionError: Network/connection error
    """
    # Ensure endpoint starts with /
    if not endpoint.startswith("/"):
      endpoint = f"/{endpoint}"

    logger.debug("API request: %s %s (params: %s)", method, endpoint, params)

    try:
      if method.upper() == "GET":
        response = await self.client.get(endpoint, params=params)
      elif method.upper() == "POST":
        response = await self.client.post(endpoint, json=params)
      else:
        raise ValueError(f"Unsupported HTTP method: {method}")

      # Raise for HTTP errors (4xx, 5xx)
      response.raise_for_status()

      # Parse JSON
      data = response.json()
      logger.debug("API response: status=%s, size=%s bytes", response.status_code, len(response.text))
      return data

    except httpx.TimeoutException as e:
      logger.warning("API timeout: %s %s (timeout=%ss)", method, endpoint, self.timeout_seconds)
      raise ApiTimeoutError(
        f"Request timed out after {self.timeout_seconds}s",
        timeout_seconds=self.timeout_seconds,
      ) from e

    except httpx.HTTPStatusError as e:
      logger.warning(
        "API HTTP error: %s %s -> %s",
        method,
        endpoint,
        e.response.status_code,
      )
      raise ApiHttpError(
        status_code=e.response.status_code,
        response_text=e.response.text,
        endpoint=endpoint,
      ) from e

    except httpx.RequestError as e:
      logger.error("API connection error: %s %s -> %s", method, endpoint, str(e))
      raise ApiConnectionError(f"Connection failed: {str(e)}") from e

  async def close(self):
    """Close the HTTP client."""
    await self.client.aclose()
    logger.debug("API client closed")

  async def __aenter__(self):
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self.close()
