from sqlalchemy.engine import URL

import os


def create_url(drivername: str) -> URL:
    return URL.create(
        drivername,
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )


def database_url_async() -> URL:
    return create_url("postgresql+asyncpg")


def database_url_sync() -> URL:
    return create_url("postgresql")
