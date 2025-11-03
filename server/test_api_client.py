"""Unit tests for ExternalApiClient."""
import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch

import httpx

from api_client import ExternalApiClient
from exceptions import ApiTimeoutError, ApiHttpError, ApiConnectionError


@pytest.fixture
def api_client():
  """Create test API client."""
  return ExternalApiClient(
    base_url="https://api.test.com",
    api_key="test-key-123",
    timeout_seconds=5.0,
  )


@pytest.mark.asyncio
async def test_fetch_json_success(api_client):
  """Test successful API call."""
  mock_response = {"data": "success", "count": 42}

  with patch.object(api_client.client, "get") as mock_get:
    mock_get.return_value = AsyncMock(
      status_code=200,
      json=lambda: mock_response,
      text='{"data": "success"}',
    )
    mock_get.return_value.raise_for_status = lambda: None

    result = await api_client.fetch_json("/test", params={"q": "hello"})

    assert result == mock_response
    mock_get.assert_called_once_with("/test", params={"q": "hello"})


@pytest.mark.asyncio
async def test_fetch_json_timeout(api_client):
  """Test timeout error."""
  with patch.object(api_client.client, "get") as mock_get:
    mock_get.side_effect = httpx.TimeoutException("Timeout")

    with pytest.raises(ApiTimeoutError) as exc_info:
      await api_client.fetch_json("/test")

    assert exc_info.value.timeout_seconds == 5.0


@pytest.mark.asyncio
async def test_fetch_json_http_error_404(api_client):
  """Test HTTP 404 error."""
  with patch.object(api_client.client, "get") as mock_get:
    # Create a mock response with proper attributes
    mock_response = Mock(status_code=404, text="Not Found")

    # Make get() return an awaitable that yields the mock response
    async def mock_get_coro(*args, **kwargs):
      return mock_response

    mock_get.side_effect = mock_get_coro

    # Configure raise_for_status to raise the exception
    def raise_status():
      raise httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=mock_response,
      )

    mock_response.raise_for_status = raise_status

    with pytest.raises(ApiHttpError) as exc_info:
      await api_client.fetch_json("/test")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_fetch_json_connection_error(api_client):
  """Test connection error."""
  with patch.object(api_client.client, "get") as mock_get:
    mock_get.side_effect = httpx.ConnectError("Connection refused")

    with pytest.raises(ApiConnectionError):
      await api_client.fetch_json("/test")


@pytest.mark.asyncio
async def test_close(api_client):
  """Test client close."""
  with patch.object(api_client.client, "aclose") as mock_close:
    await api_client.close()
    mock_close.assert_called_once()


if __name__ == "__main__":
  # Run with: python -m pytest test_api_client.py -v
  pytest.main([__file__, "-v"])
