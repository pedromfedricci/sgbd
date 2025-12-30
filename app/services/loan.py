from app.db.models.loan import Loan
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository
from app.repositories.user import UserRepository

from app.exceptions.domain import (
    UserNotFound,
    BookNotFound,
    LoanNotFound,
    BookAlreadyLoaned,
    MaxActiveLoansExceeded,
    LoanAlreadyReturned,
)

from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError
from typing import Sequence

LOAN_DAYS: int = 14
MAX_ACTIVE_LOANS: int = 3
DAILY_FINE_CENTS: int = 200


class LoanService:
    def __init__(
        self, loans: LoanRepository, users: UserRepository, books: BookRepository
    ):
        self.loans = loans
        self.users = users
        self.books = books

    async def list_by_user(self, user_id: int) -> Sequence[Loan]:
        if not await self.users.exists(user_id):
            raise UserNotFound(user_id=user_id)

        return await self.loans.list_by_user(user_id)

    async def create(self, user_id: int, book_id: int) -> Loan:
        if not await self.users.exists(user_id):
            raise UserNotFound(user_id=user_id)

        if not await self.books.exists(book_id):
            raise BookNotFound(book_id=book_id)

        active = await self.loans.count_active_by_user(user_id)

        if active >= MAX_ACTIVE_LOANS:
            raise MaxActiveLoansExceeded(user_id=user_id, active=active)

        now = datetime.now(timezone.utc)
        due_to = now + timedelta(days=LOAN_DAYS)
        loan = Loan(user_id=user_id, book_id=book_id, due_to=due_to)

        try:
            return await self.loans.add(loan)
        except IntegrityError as exc:
            raise BookAlreadyLoaned(book_id=book_id) from exc

    async def fulfill(self, loan_id: int) -> Loan:
        loan = await self.loans.get_by_id(loan_id)

        if not loan:
            raise LoanNotFound(loan_id=loan_id)

        if loan.returned_at is not None:
            raise LoanAlreadyReturned(loan_id=loan_id)

        now = datetime.now(timezone.utc)
        loan.returned_at = now

        if now > loan.due_to:
            days_late = (now.date() - loan.due_to.date()).days
            loan.fine_cents = days_late * DAILY_FINE_CENTS

        return loan

    async def list_active(self, offset: int, limit: int) -> Sequence[Loan]:
        return await self.loans.list_active(offset=offset, limit=limit)

    async def list_overdue(self, offset: int, limit: int) -> Sequence[Loan]:
        return await self.loans.list_overdue(offset=offset, limit=limit)
