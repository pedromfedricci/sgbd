import os

REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", "6379"))

CACHE_REDIS_TTL: int = 300  # 5 minutes
CACHE_MEMORY_TTL: int = 60  # 60 seconds
CACHE_MEMORY_MAXSIZE: int = 1000
