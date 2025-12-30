from app.db.models.user import User
from app.db.models.loan import Loan
from app.exceptions.domain import EmailAlreadyRegistered, UserNotFound
from app.repositories.user import UserRepository

from typing import Sequence


class UserService:
    def __init__(self, users: UserRepository):
        self.users = users

    async def list_all(self, *, offset: int, limit: int) -> Sequence[User]:
        return await self.users.list(offset=offset, limit=limit)

    async def create(self, *, name: str, email: str) -> User:
        user = await self.users.get_by_email(email)

        if user:
            raise EmailAlreadyRegistered(email=email)

        user = User(name=name, email=email)
        return await self.users.create(user)

    async def get_by_id(self, user_id: int) -> User:
        user = await self.users.get_by_id(user_id)

        if not user:
            raise UserNotFound(user_id=user_id)

        return user

    async def get_loans(self, user_id: int) -> Sequence[Loan]:
        user = await self.get_by_id(user_id)

        if not user:
            raise UserNotFound(user_id=user_id)

        return await self.users.get_loans(user_id)
