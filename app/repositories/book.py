from app.db.models.book import Book

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import exists
from typing import Sequence


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, book_id: int) -> bool:
        stmt = select(exists().where(Book.id == book_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, book_id: int) -> Book | None:
        stmt = select(Book).where(Book.id == book_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, *, offset: int, limit: int) -> Sequence[Book]:
        order_by = select(Book).order_by(Book.id)
        stmt = order_by.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, book: Book) -> Book:
        self.session.add(book)
        await self.session.flush()
        return book
