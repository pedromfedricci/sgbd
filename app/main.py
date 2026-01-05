from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.exception_handlers import app_exception_handler
from app.api.middleware import LoggingMiddleware
from app.api.v1.router import router as api_router
from app.exceptions.domain import AppException
from app.lifespan import lifespan
from app.logging import configure_logging
from app.tracing import configure_tracing

TITLE: str = "API do sistema de gerenciamento de biblioteca digital"

configure_logging()
configure_tracing()

app = FastAPI(title=TITLE, lifespan=lifespan)
app.add_middleware(LoggingMiddleware)
app.include_router(api_router)
app.add_exception_handler(AppException, app_exception_handler)
FastAPIInstrumentor.instrument_app(app)
