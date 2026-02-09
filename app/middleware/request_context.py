"""
Request context middleware for logging.

Automatically injects request ID and trace ID into all logs
generated during request processing.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import generate_request_id, set_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set request context for logging."""

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request/trace IDs
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        trace_id = request.headers.get("X-Trace-ID") or generate_request_id()

        # Set context for logging
        set_request_context(request_id=request_id, trace_id=trace_id)

        # Process request
        response = await call_next(request)

        # Add request ID to response headers for tracing
        response.headers["X-Request-ID"] = request_id

        return response
