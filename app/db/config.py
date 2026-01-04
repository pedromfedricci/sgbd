import os

from sqlalchemy.engine import URL


def create_url(drivername: str) -> URL:
    return URL.create(
        drivername,
        username=os.environ.get("DB_USER", ""),
        password=os.environ.get("DB_PASSWORD", ""),
        host=os.environ.get("DB_HOST", ""),
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ.get("DB_NAME", ""),
    )


def database_url_async() -> URL:
    return create_url("postgresql+asyncpg")


def database_url_sync() -> URL:
    return create_url("postgresql")
