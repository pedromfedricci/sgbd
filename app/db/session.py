from app.db.config import database_url_async

import structlog
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

engine = create_async_engine(database_url_async(), echo=True, future=True)
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

logger = structlog.get_logger("sgbd.db.session")


async def get_db_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error("transaction_rolled_back", err=str(exc), exc_info=True)
            raise
