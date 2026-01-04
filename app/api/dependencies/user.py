from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db_async_session
from app.repositories.user import UserRepository
from app.services.user import UserService


def user_service() -> UserService:
    def service(s: AsyncSession = get_db_async_session()) -> UserService:
        return UserService(UserRepository(s))

    return Depends(service)
