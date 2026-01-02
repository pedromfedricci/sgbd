from app.exceptions.domain import (
    AppException,
    EmailAlreadyRegistered,
    LoanAlreadyReturned,
    LoanNotFound,
    UserNotFound,
    BookNotFound,
    BookAlreadyLoaned,
    MaxActiveLoansExceeded,
)

import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi import status

logger = structlog.get_logger("sgbd.api.exceptions")

ERROR_MAP = {
    UserNotFound: (status.HTTP_404_NOT_FOUND, "User not found"),
    BookNotFound: (status.HTTP_404_NOT_FOUND, "Book not found"),
    LoanNotFound: (status.HTTP_404_NOT_FOUND, "Loan not found"),
    BookAlreadyLoaned: (status.HTTP_409_CONFLICT, "Book already loaned"),
    EmailAlreadyRegistered: (status.HTTP_409_CONFLICT, "Email already registered"),
    LoanAlreadyReturned: (status.HTTP_409_CONFLICT, "Loan already returned"),
    MaxActiveLoansExceeded: (status.HTTP_409_CONFLICT, "Max active loans exceeded"),
}

UNKNOWN_ERROR: tuple[int, str] = (
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "Unknown error",
)


def map_error(exc: AppException) -> tuple[int, str]:
    return ERROR_MAP.get(type(exc), UNKNOWN_ERROR)


def app_exception_handler(_: Request, exc: AppException) -> Response:
    status_code, detail = map_error(exc)

    log_method = logger.warning if status_code < 500 else logger.error
    log_method(
        "domain_exception",
        exception_type=type(exc).__name__,
        code=exc.code,
        status_code=status_code,
        **exc.context,
    )

    content = {
        "detail": detail,
        "code": exc.code,
        "context": exc.context,
    }
    return JSONResponse(content, status_code)
