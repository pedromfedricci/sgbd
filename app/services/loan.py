from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

import structlog
from opentelemetry import trace
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from app.db.models.loan import Loan
from app.exceptions.domain import (
    BookNotFound,
    LoanAlreadyReturned,
    LoanConcurrentModification,
    LoanNotFound,
    MaxActiveLoansExceeded,
    NoCopiesAvailable,
    UserNotFound,
)
from app.repositories.book import BookRepository
from app.repositories.book_copy import BookCopyRepository
from app.repositories.loan import LoanRepository
from app.repositories.user import UserRepository

LOAN_DAYS: int = 14
MAX_ACTIVE_LOANS: int = 3
DAILY_FINE_CENTS: int = 200

logger = structlog.get_logger("sgbd.services.loan")
tracer = trace.get_tracer("sgbd.services.loan")


class LoanService:
    def __init__(
        self,
        loans: LoanRepository,
        users: UserRepository,
        books: BookRepository,
        copies: BookCopyRepository,
    ):
        self.loans = loans
        self.users = users
        self.books = books
        self.copies = copies

    async def list_by_user(self, user_id: int) -> Sequence[Loan]:
        structlog.contextvars.bind_contextvars(user_id=user_id)

        with tracer.start_as_current_span("LoanService.list_by_user") as span:
            span.set_attribute("user_id", user_id)

            if not await self.users.exists(user_id):
                logger.warning("user_not_found", user_id=user_id)
                raise UserNotFound(user_id=user_id)

            loans = await self.loans.list_by_user(user_id)
            span.set_attribute("loan_count", len(loans))
            return loans

    async def create(self, user_id: int, book_id: int) -> Loan:
        structlog.contextvars.bind_contextvars(user_id=user_id, book_id=book_id)

        with tracer.start_as_current_span("LoanService.create") as span:
            span.set_attribute("user_id", user_id)
            span.set_attribute("book_id", book_id)

            if not await self.books.exists(book_id):
                logger.warning("loan_creation_failed", reason="book_not_found")
                raise BookNotFound(book_id=book_id)

            # Lock user row to serialize concurrent loan creation per user
            user = await self.users.get_for_update(user_id)
            if not user:
                logger.warning("loan_creation_failed", reason="user_not_found")
                raise UserNotFound(user_id=user_id)

            active = await self.loans.count_active_by_user(user_id)
            span.set_attribute("active_loans", active)

            if active >= MAX_ACTIVE_LOANS:
                logger.warning(
                    "loan_creation_failed",
                    reason="max_loans_exceeded",
                    active=active,
                    max_allowed=MAX_ACTIVE_LOANS,
                )
                raise MaxActiveLoansExceeded(user_id=user_id, active=active)

            # Find an available copy
            copy = await self.copies.get_available_for_book(book_id)
            if not copy:
                logger.warning("loan_creation_failed", reason="no_copies_available")
                raise NoCopiesAvailable(book_id=book_id)

            span.set_attribute("copy_id", copy.id)

            now = datetime.now(UTC)
            due_to = now + timedelta(days=LOAN_DAYS)
            loan = Loan(user_id=user_id, copy_id=copy.id, due_to=due_to)

            try:
                created = await self.loans.save(loan)
                span.set_attribute("loan_id", created.id)
                logger.info(
                    "loan_created",
                    loan_id=created.id,
                    copy_id=copy.id,
                    due_to=due_to.isoformat(),
                )
                return created
            except IntegrityError as exc:
                # Concurrent request took this copy
                logger.warning("loan_creation_failed", reason="no_copies_available")
                raise NoCopiesAvailable(book_id=book_id) from exc

    async def fulfill(self, loan_id: int) -> Loan:
        structlog.contextvars.bind_contextvars(loan_id=loan_id)

        with tracer.start_as_current_span("LoanService.fulfill") as span:
            span.set_attribute("loan_id", loan_id)

            loan = await self.loans.get_by_id(loan_id)

            if not loan:
                logger.warning("loan_return_failed", reason="loan_not_found")
                raise LoanNotFound(loan_id=loan_id)

            span.set_attribute("user_id", loan.user_id)
            span.set_attribute("copy_id", loan.copy_id)
            structlog.contextvars.bind_contextvars(
                user_id=loan.user_id, copy_id=loan.copy_id
            )

            if loan.returned_at is not None:
                logger.warning("loan_return_failed", reason="already_returned")
                raise LoanAlreadyReturned(loan_id=loan_id)

            now = datetime.now(UTC)
            loan.returned_at = now

            if now > loan.due_to:
                days_late = (now.date() - loan.due_to.date()).days
                loan.fine_cents = days_late * DAILY_FINE_CENTS
                span.set_attribute("days_late", days_late)
                span.set_attribute("fine_cents", loan.fine_cents)
                logger.info(
                    "loan_returned_late",
                    days_late=days_late,
                    fine_cents=loan.fine_cents,
                )
            else:
                logger.info("loan_returned_on_time")

            try:
                return await self.loans.save(loan)
            except StaleDataError as exc:
                logger.warning("loan_return_failed", reason="concurrent_modification")
                raise LoanConcurrentModification(loan_id=loan_id) from exc

    async def list_active(self, offset: int, limit: int) -> Sequence[Loan]:
        with tracer.start_as_current_span("LoanService.list_active") as span:
            span.set_attribute("offset", offset)
            span.set_attribute("limit", limit)
            loans = await self.loans.list_active(offset=offset, limit=limit)
            span.set_attribute("result_count", len(loans))
            return loans

    async def list_overdue(self, offset: int, limit: int) -> Sequence[Loan]:
        with tracer.start_as_current_span("LoanService.list_overdue") as span:
            span.set_attribute("offset", offset)
            span.set_attribute("limit", limit)
            loans = await self.loans.list_overdue(offset=offset, limit=limit)
            span.set_attribute("result_count", len(loans))
            return loans
