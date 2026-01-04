from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_db_async_session() -> AsyncSession:
    from app.db.session import get_db_async_session

    return Depends(get_db_async_session)
