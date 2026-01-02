from typing import Any


class AppException(Exception):
    code: str = "domain_error"

    def __init__(self, **cxt: Any):
        self.context = cxt
        super().__init__()


class UserNotFound(AppException):
    code: str = "user_not_found"


class EmailAlreadyRegistered(AppException):
    code: str = "email_already_registered"


class BookNotFound(AppException):
    code: str = "book_not_found"


class BookAlreadyLoaned(AppException):
    code: str = "book_already_loaned"


class LoanNotFound(AppException):
    code: str = "loan_not_found"


class LoanAlreadyReturned(AppException):
    code: str = "loan_already_returned"


class MaxActiveLoansExceeded(AppException):
    code: str = "max_active_loans_exceeded"
