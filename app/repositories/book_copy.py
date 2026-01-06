from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import exists

from app.db.models.book_copy import BookCopy
from app.db.models.loan import Loan


class BookCopyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, copy_id: int) -> bool:
        stmt = select(exists().where(BookCopy.id == copy_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, copy_id: int) -> BookCopy | None:
        stmt = select(BookCopy).where(BookCopy.id == copy_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_book(self, book_id: int) -> Sequence[BookCopy]:
        stmt = select(BookCopy).where(BookCopy.book_id == book_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_available_for_book(self, book_id: int) -> BookCopy | None:
        active = select(Loan.copy_id).where(Loan.returned_at.is_(None))
        active_sub = active.scalar_subquery()
        stmt = (
            select(BookCopy)
            .where(BookCopy.book_id == book_id)
            .where(BookCopy.id.not_in(active_sub))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, copy: BookCopy) -> BookCopy:
        self.session.add(copy)
        await self.session.flush()
        return copy
