"""Rate limiting middleware for request throttling."""
from __future__ import annotations

import time
import logging
from typing import Dict, Tuple
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.

    Limits requests per client IP address within a time window.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        enabled: bool = True,
    ):
        """Initialize rate limiter.

        Args:
            app: ASGI application
            requests_per_minute: Maximum requests allowed per minute per IP
            enabled: Whether rate limiting is enabled
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.enabled = enabled
        self.window_seconds = 60
        # {ip: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        logger.info(
            f"Rate limiting {'enabled' if enabled else 'disabled'}: "
            f"{requests_per_minute} requests/minute"
        )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request.

        Checks X-Forwarded-For header for proxy setups.
        """
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP in the chain
            return forwarded.split(",")[0].strip()

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _clean_old_requests(self, ip: str, current_time: float) -> None:
        """Remove requests older than the time window."""
        cutoff = current_time - self.window_seconds
        self._requests[ip] = [
            req for req in self._requests[ip] if req[0] > cutoff
        ]

    def _is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        """Check if client is rate limited.

        Returns:
            Tuple of (is_limited, remaining_requests)
        """
        current_time = time.time()
        self._clean_old_requests(ip, current_time)

        request_count = len(self._requests[ip])
        remaining = max(0, self.requests_per_minute - request_count)

        if request_count >= self.requests_per_minute:
            return True, 0

        # Record this request
        self._requests[ip].append((current_time,))
        return False, remaining - 1

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting if disabled
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        is_limited, remaining = self._is_rate_limited(client_ip)

        if is_limited:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later.",
                    "retry_after_seconds": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Process request and add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
