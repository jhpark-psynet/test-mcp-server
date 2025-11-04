"""Custom exceptions for MCP server."""


class ApiError(Exception):
  """Base exception for API errors."""
  pass


class ApiTimeoutError(ApiError):
  """API request timeout."""
  def __init__(self, message: str, timeout_seconds: float):
    self.timeout_seconds = timeout_seconds
    super().__init__(message)


class ApiHttpError(ApiError):
  """HTTP error from API."""
  def __init__(self, status_code: int, response_text: str, endpoint: str):
    self.status_code = status_code
    self.response_text = response_text
    self.endpoint = endpoint
    super().__init__(f"HTTP {status_code}: {response_text[:100]}")


class ApiConnectionError(ApiError):
  """Connection error to API."""
  pass
