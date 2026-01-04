from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db_async_session
from app.repositories import BookRepository, LoanRepository, UserRepository
from app.services.loan import LoanService


def loan_service() -> LoanService:
    def service(s: AsyncSession = get_db_async_session()) -> LoanService:
        return LoanService(LoanRepository(s), UserRepository(s), BookRepository(s))

    return Depends(service)
