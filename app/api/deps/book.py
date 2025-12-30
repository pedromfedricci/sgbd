from app.services.book import BookService
from app.repositories.book import BookRepository
from app.deps.db import get_db_async_session

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


def book_service() -> BookService:
    def service(s: AsyncSession = get_db_async_session()) -> BookService:
        return BookService(BookRepository(s))

    return Depends(service)
