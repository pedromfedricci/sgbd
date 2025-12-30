from app.db.config import database_url_async

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

engine = create_async_engine(database_url_async(), echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
