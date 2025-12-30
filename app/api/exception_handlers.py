from app.exceptions.domain import (
    AppException,
    EmailAlreadyRegistered,
    UserNotFound,
    BookNotFound,
    MaxActiveLoansExceeded,
)

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi import status

ERROR_MAP = {
    UserNotFound: (status.HTTP_404_NOT_FOUND, "User not found"),
    BookNotFound: (status.HTTP_404_NOT_FOUND, "Book not found"),
    EmailAlreadyRegistered: (status.HTTP_409_CONFLICT, "Email already registered"),
    MaxActiveLoansExceeded: (status.HTTP_409_CONFLICT, "Loan limit reached"),
}

UNKNOWN_ERROR: tuple[int, str] = (
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "Unknown error",
)


def map_error(exc: AppException) -> tuple[int, str]:
    return ERROR_MAP.get(type(exc), UNKNOWN_ERROR)


def app_exception_handler(_: Request, exc: AppException) -> Response:
    status, detail = map_error(exc)
    content = {
        "detail": detail,
        "code": exc.code,
        "context": exc.context,
    }
    return JSONResponse(content, status)
