"""Rate limiting middleware using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.utils.logger import logger

# Create global limiter instance
limiter = Limiter(key_func=get_remote_address)


def rate_limit_error_handler(request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)}: {exc.detail}"
    )
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "retry_after": (
                exc.detail.split("per ")[1] if "per " in exc.detail else "unknown"
            ),
        },
    )
