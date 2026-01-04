import time
import uuid

import structlog
from fastapi import Request, Response
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_PT_HEADER = "X-Process-TIME"


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = structlog.get_logger("sgbd.api.http")

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("request.id", request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            self.logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers[REQUEST_PT_HEADER] = str(duration_ms)
            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.logger.exception(
                "request_failed",
                duration_ms=round(duration_ms, 2),
                exc_type=type(exc).__name__,
            )
            raise
