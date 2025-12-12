"""Standardized API error handling with user-friendly messages."""
from enum import Enum
from typing import Dict, List, Any


class APIErrorCode(Enum):
    """Error codes for API operations."""
    TIMEOUT = "TIMEOUT"
    NOT_FOUND = "NOT_FOUND"
    SERVER_ERROR = "SERVER_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN = "UNKNOWN"


ERROR_MESSAGES: Dict[APIErrorCode, str] = {
    APIErrorCode.TIMEOUT: "The server is taking too long to respond. Please try again later.",
    APIErrorCode.NOT_FOUND: "The requested data could not be found.",
    APIErrorCode.SERVER_ERROR: "The external service is temporarily unavailable. Please try again later.",
    APIErrorCode.CONNECTION_ERROR: "Unable to connect to the server. Please check your network connection.",
    APIErrorCode.VALIDATION_ERROR: "The input provided is invalid.",
    APIErrorCode.UNKNOWN: "An unexpected error occurred. Please try again later.",
}


class APIError(Exception):
    """Exception for API errors with user-friendly messages.

    Attributes:
        code: Error code enum value
        detail: Technical details for logging (not shown to users)
        user_message: User-friendly message to display
    """

    def __init__(self, code: APIErrorCode, detail: str = ""):
        self.code = code
        self.detail = detail
        self.user_message = ERROR_MESSAGES[code]
        super().__init__(self.user_message)

    def __str__(self) -> str:
        return self.user_message

    def __repr__(self) -> str:
        return f"APIError(code={self.code.value}, detail={self.detail!r})"


def format_validation_errors(errors: List[Dict[str, Any]]) -> str:
    """Convert Pydantic validation errors to user-friendly message.

    Args:
        errors: List of Pydantic error dicts from ValidationError.errors()

    Returns:
        User-friendly error message string
    """
    if not errors:
        return "The input provided is invalid."

    messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        error_type = error.get("type", "")

        if error_type == "missing":
            messages.append(f"'{field}' is required")
        elif error_type == "string_pattern_mismatch":
            messages.append(f"'{field}' has invalid format")
        elif error_type == "enum":
            messages.append(f"'{field}' has invalid value")
        elif error_type == "string_too_short":
            messages.append(f"'{field}' is too short")
        elif error_type == "string_too_long":
            messages.append(f"'{field}' is too long")
        else:
            messages.append(f"'{field}' is invalid")

    return "Invalid input: " + "; ".join(messages)
