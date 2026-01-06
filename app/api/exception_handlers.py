import structlog
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app.exceptions.domain import (
    AppException,
    BookAlreadyExists,
    BookNotFound,
    EmailAlreadyRegistered,
    LoanAlreadyReturned,
    LoanConcurrentModification,
    LoanNotFound,
    MaxActiveLoansExceeded,
    NoCopiesAvailable,
    UserNotFound,
)

logger = structlog.get_logger("sgbd.api.exceptions")

ERROR_MAP = {
    UserNotFound: (status.HTTP_404_NOT_FOUND, "User not found"),
    BookNotFound: (status.HTTP_404_NOT_FOUND, "Book not found"),
    LoanNotFound: (status.HTTP_404_NOT_FOUND, "Loan not found"),
    BookAlreadyExists: (status.HTTP_409_CONFLICT, "Book already exists"),
    EmailAlreadyRegistered: (status.HTTP_409_CONFLICT, "Email already registered"),
    LoanAlreadyReturned: (status.HTTP_409_CONFLICT, "Loan already returned"),
    LoanConcurrentModification: (
        status.HTTP_409_CONFLICT,
        "Loan was modified concurrently",
    ),
    MaxActiveLoansExceeded: (status.HTTP_409_CONFLICT, "Max active loans exceeded"),
    NoCopiesAvailable: (status.HTTP_409_CONFLICT, "No copies available for loan"),
}

UNKNOWN_ERROR: tuple[int, str] = (
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "Unknown error",
)


def map_error(exc: AppException) -> tuple[int, str]:
    return ERROR_MAP.get(type(exc), UNKNOWN_ERROR)


def app_exception_handler(_: Request, exc: Exception) -> Response:
    assert isinstance(exc, AppException)
    status_code, detail = map_error(exc)

    log = logger.warning if status_code < 500 else logger.error
    log(
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
