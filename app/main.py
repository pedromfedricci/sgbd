from app.api.v1.router import router as api_router
from app.exceptions.domain import AppException

from fastapi import FastAPI
from fastapi import Request, Response

app = FastAPI(title="API do sistema de gerenciamento de biblioteca digital")
app.include_router(api_router)


@app.exception_handler(AppException)
async def app_exception_handler(r: Request, e: AppException) -> Response:
    from app.api.exception_handlers import app_exception_handler

    return app_exception_handler(r, e)
