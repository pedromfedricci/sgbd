from app.api.v1 import users
from app.api.v1 import books
from app.api.v1 import loans

from fastapi import APIRouter

router = APIRouter()

router.include_router(users.router)
router.include_router(books.router)
router.include_router(loans.router)
