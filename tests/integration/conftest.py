from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

import app.db.models  # noqa: F401 - registers models with Base.metadata
from app.db.base import Base
from app.db.session import get_db_async_session


@pytest.fixture(scope="session")
def postgres() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture
async def engine(postgres: PostgresContainer) -> AsyncGenerator[AsyncEngine]:
    url = postgres.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient]:
    from app.main import app

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_session():
        async with session_factory() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_db_async_session] = override_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
