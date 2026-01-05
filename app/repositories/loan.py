from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.loan import Loan


class LoanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, loan_id: int) -> Loan | None:
        stmt = select(Loan).where(Loan.id == loan_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> Sequence[Loan]:
        stmt = select(Loan).where(Loan.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def active_loan_for_book(self, book_id: int) -> Loan | None:
        was_loaned = Loan.book_id == book_id
        returned = Loan.returned_at.is_(None)
        stmt = select(Loan).where(was_loaned, returned)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_active_by_user(self, user_id: int) -> int:
        was_loaned = Loan.user_id == user_id
        returned = Loan.returned_at.is_(None)
        count_from = select(func.count()).select_from(Loan)
        stmt = count_from.where(was_loaned, returned)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list_active(self, *, offset: int, limit: int) -> Sequence[Loan]:
        active = select(Loan).where(Loan.returned_at.is_(None))
        order_by = active.order_by(Loan.due_to.asc(), Loan.id.asc())
        stmt = order_by.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_overdue(self, *, offset: int, limit: int) -> Sequence[Loan]:
        returned = Loan.returned_at.is_(None)
        is_due = Loan.due_to < func.now()
        overdue = select(Loan).where(returned, is_due)
        order_by = overdue.order_by(Loan.due_to.asc(), Loan.id.asc())
        stmt = order_by.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save(self, loan: Loan) -> Loan:
        self.session.add(loan)
        await self.session.flush()
        return loan
