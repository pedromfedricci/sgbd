from collections.abc import Awaitable
from typing import cast

import structlog
from redis.asyncio import ConnectionPool, Redis

from app.cache.config import REDIS_HOST, REDIS_PORT

logger = structlog.get_logger("sgbd.cache.client")

_pool: ConnectionPool | None = None
_client: Redis | None = None


async def init_redis() -> None:
    global _pool, _client

    try:
        _pool = ConnectionPool.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}",
            max_connections=10,
            decode_responses=True,
        )
        _client = Redis(connection_pool=_pool)
        await cast(Awaitable[bool], _client.ping())
        logger.info("redis_connected", host=REDIS_HOST, port=REDIS_PORT)
    except Exception:
        logger.warning("redis_unavailable", host=REDIS_HOST, port=REDIS_PORT)
        _pool = None
        _client = None


async def close_redis() -> None:
    global _pool, _client

    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("redis_disconnected")

    if _pool is not None:
        await _pool.disconnect()
        _pool = None


def get_redis_client() -> Redis | None:
    return _client
