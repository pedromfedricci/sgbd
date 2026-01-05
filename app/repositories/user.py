from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import exists

from app.db.models.loan import Loan
from app.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, *, offset: int, limit: int) -> Sequence[User]:
        order_by = select(User).order_by(User.id)
        stmt = order_by.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def exists(self, user_id: int) -> bool:
        stmt = select(exists().where(User.id == user_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_for_update(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_loans(self, user_id: int) -> Sequence[Loan]:
        stmt = select(Loan).where(Loan.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
