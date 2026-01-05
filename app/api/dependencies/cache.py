from fastapi import Depends

from app.cache.book import BookCache
from app.cache.client import get_redis_client


def get_book_cache() -> BookCache:
    def get_book_cache() -> BookCache:
        return BookCache(get_redis_client())

    return Depends(get_book_cache)
