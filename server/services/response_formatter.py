"""API 응답 포맷팅 유틸리티."""
from typing import Any, Dict
import json


def format_api_response_text(data: Dict[str, Any], endpoint: str) -> str:
    """Format successful API response as text.

    Args:
        data: JSON response data from API
        endpoint: API endpoint that was called

    Returns:
        Formatted text string
    """
    lines = [
        "API Response Success",
        f"Endpoint: {endpoint}",
        "",
        "Summary:",
    ]

    # Add basic stats
    if isinstance(data, dict):
        lines.append(f"  - Keys: {len(data)}")
        lines.append(f"  - Top-level fields: {', '.join(list(data.keys())[:5])}")
    elif isinstance(data, list):
        lines.append(f"  - Items: {len(data)}")
        if data and isinstance(data[0], dict):
            lines.append(f"  - Item fields: {', '.join(list(data[0].keys())[:5])}")

    lines.extend([
        "",
        "Full Response:",
        "```json",
        json.dumps(data, indent=2, ensure_ascii=False)[:2000],  # Limit to 2000 chars
        "```",
    ])

    return "\n".join(lines)


def format_api_error_text(error: Exception, endpoint: str) -> str:
    """Format API error as text.

    Args:
        error: Exception that occurred
        endpoint: API endpoint that was called

    Returns:
        Formatted error text
    """
    from server.services.exceptions import ApiTimeoutError, ApiHttpError, ApiConnectionError

    lines = [
        "❌ API Request Failed",
        f"Endpoint: {endpoint}",
        "",
    ]

    if isinstance(error, ApiTimeoutError):
        lines.extend([
            "Error Type: Timeout",
            f"Timeout: {error.timeout_seconds}s",
            "The API did not respond within the configured timeout period.",
        ])
    elif isinstance(error, ApiHttpError):
        lines.extend([
            f"Error Type: HTTP {error.status_code}",
            f"Status Code: {error.status_code}",
            f"Response: {error.response_text[:500]}",
        ])
    elif isinstance(error, ApiConnectionError):
        lines.extend([
            "Error Type: Connection Error",
            f"Details: {str(error)}",
            "Could not connect to the API server.",
        ])
    else:
        lines.extend([
            "Error Type: Unknown",
            f"Details: {str(error)}",
        ])

    return "\n".join(lines)
