"""FastAPI metrics middleware for Prometheus monitoring"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.utils.metrics import api_requests_total, api_request_duration
from app.utils.logger import logger


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record API request metrics"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Record metrics for each request"""
        # Record start time
        start_time = time.time()

        # Extract endpoint info
        method = request.method
        endpoint = request.url.path

        # Call next middleware/handler
        response = await call_next(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Record metrics
        try:
            api_requests_total.labels(
                method=method, endpoint=endpoint, status=response.status_code
            ).inc()

            api_request_duration.labels(method=method, endpoint=endpoint).observe(
                duration
            )

            # Add process time header
            response.headers["X-Process-Time"] = str(duration)

        except Exception as e:
            logger.error(f"Error recording metrics: {str(e)}", exc_info=True)

        return response
