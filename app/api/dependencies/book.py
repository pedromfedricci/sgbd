from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db_async_session
from app.repositories.book import BookRepository
from app.services.book import BookService


def book_service() -> BookService:
    def service(s: AsyncSession = get_db_async_session()) -> BookService:
        return BookService(BookRepository(s))

    return Depends(service)
