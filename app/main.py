from app.api.middleware import LoggingMiddleware
from app.api.v1.router import router as api_router
from app.exceptions.domain import AppException
from app.logging import configure_logging
from app.tracing import configure_tracing

from fastapi import FastAPI
from fastapi import Request, Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

configure_logging()
configure_tracing()

app = FastAPI(title="API do sistema de gerenciamento de biblioteca digital")
app.add_middleware(LoggingMiddleware)
app.include_router(api_router)
FastAPIInstrumentor.instrument_app(app)


@app.exception_handler(AppException)
async def app_exception_handler(r: Request, e: AppException) -> Response:
    from app.api.exception_handlers import app_exception_handler

    return app_exception_handler(r, e)
