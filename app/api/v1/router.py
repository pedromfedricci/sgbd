from fastapi import APIRouter

from app.api import health
from app.api.v1 import books, loans, users

router = APIRouter()

router.include_router(health.router)
router.include_router(users.router)
router.include_router(books.router)
router.include_router(loans.router)
