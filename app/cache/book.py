import json

import structlog
from cachetools import TTLCache
from redis.asyncio import Redis

from app.cache.config import (
    CACHE_MEMORY_MAXSIZE,
    CACHE_MEMORY_TTL,
    CACHE_REDIS_TTL,
)
from app.db.models.book import Book

logger = structlog.get_logger("sgbd.cache.book")


def _cache_key(book_id: int) -> str:
    return f"book:{book_id}"


def _serialize(book: Book) -> str:
    return json.dumps({"id": book.id, "title": book.title, "author": book.author})


def _deserialize(data: str) -> Book:
    obj = json.loads(data)
    book = Book(id=obj["id"], title=obj["title"], author=obj["author"])
    return book


class BookCache:
    def __init__(self, redis: Redis | None):
        self._redis = redis
        self._memory: TTLCache[str, Book] = TTLCache(
            maxsize=CACHE_MEMORY_MAXSIZE, ttl=CACHE_MEMORY_TTL
        )

    async def get(self, book_id: int) -> Book | None:
        key = _cache_key(book_id)

        # Check in-memory cache first
        if key in self._memory:
            logger.debug("cache_hit_memory", book_id=book_id)
            return self._memory[key]

        # Check Redis if available
        if self._redis is not None:
            try:
                data = await self._redis.get(key)
                if data is not None:
                    book = _deserialize(data)
                    self._memory[key] = book
                    logger.debug("cache_hit_redis", book_id=book_id)
                    return book
            except Exception:
                logger.warning("redis_get_failed", book_id=book_id, exc_info=True)

        logger.debug("cache_miss", book_id=book_id)
        return None

    async def set(self, book: Book) -> None:
        key = _cache_key(book.id)

        # Always set in-memory
        self._memory[key] = book

        # Set in Redis if available
        if self._redis is not None:
            try:
                data = _serialize(book)
                await self._redis.set(key, data, ex=CACHE_REDIS_TTL)
                logger.debug("cache_set", book_id=book.id)
            except Exception:
                logger.warning("redis_set_failed", book_id=book.id, exc_info=True)

    async def delete(self, book_id: int) -> None:
        key = _cache_key(book_id)

        # Only delete from Redis; in-memory expires via TTL
        if self._redis is not None:
            try:
                await self._redis.delete(key)
                logger.debug("cache_delete", book_id=book_id)
            except Exception:
                logger.warning("redis_delete_failed", book_id=book_id, exc_info=True)
