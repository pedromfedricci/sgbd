from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db_async_session
from app.repositories.book import BookRepository
from app.repositories.book_copy import BookCopyRepository
from app.repositories.loan import LoanRepository
from app.repositories.user import UserRepository
from app.services.loan import LoanService


def loan_service() -> LoanService:
    def service(s: AsyncSession = get_db_async_session()) -> LoanService:
        return LoanService(
            LoanRepository(s),
            UserRepository(s),
            BookRepository(s),
            BookCopyRepository(s),
        )

    return Depends(service)
