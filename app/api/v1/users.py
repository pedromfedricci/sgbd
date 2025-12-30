from app.api.deps.user import user_service
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.loan import LoanResponse

from fastapi import APIRouter, status

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    offset: int = 0, limit: int = 10, users: UserService = user_service()
):
    return await users.list_all(offset=offset, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, users: UserService = user_service()):
    return await users.get_by_id(user_id)


@router.get("/{user_id}/loans", response_model=list[LoanResponse])
async def get_user_loans(user_id: int, users: UserService = user_service()):
    return await users.get_loans(user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, users: UserService = user_service()):
    return await users.create(name=user.name, email=user.email)
