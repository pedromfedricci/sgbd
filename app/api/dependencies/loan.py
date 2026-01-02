from app.services.loan import LoanService
from app.repositories import LoanRepository, UserRepository, BookRepository
from app.api.dependencies.db import get_db_async_session

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


def loan_service() -> LoanService:
    def service(s: AsyncSession = get_db_async_session()) -> LoanService:
        return LoanService(LoanRepository(s), UserRepository(s), BookRepository(s))

    return Depends(service)
