from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.cache.client import close_redis, init_redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_redis()
    yield
    await close_redis()
