from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.cache import get_book_cache
from app.api.dependencies.db import get_db_async_session
from app.cache.book import BookCache
from app.repositories.book import BookRepository
from app.services.book import BookService


def book_service() -> BookService:
    def service(
        s: AsyncSession = get_db_async_session(),
        c: BookCache = get_book_cache(),
    ) -> BookService:
        return BookService(BookRepository(s), c)

    return Depends(service)
