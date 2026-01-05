from collections.abc import Sequence

import structlog
from opentelemetry import trace
from sqlalchemy.exc import IntegrityError

from app.db.models.loan import Loan
from app.db.models.user import User
from app.exceptions.domain import EmailAlreadyRegistered, UserNotFound
from app.repositories.user import UserRepository

logger = structlog.get_logger("sgbd.services.user")
tracer = trace.get_tracer("sgbd.services.user")


class UserService:
    def __init__(self, users: UserRepository):
        self.users = users

    async def list_all(self, *, offset: int, limit: int) -> Sequence[User]:
        with tracer.start_as_current_span("UserService.list_all") as span:
            span.set_attribute("offset", offset)
            span.set_attribute("limit", limit)
            users = await self.users.list(offset=offset, limit=limit)
            span.set_attribute("result_count", len(users))
            return users

    async def create(self, *, name: str, email: str) -> User:
        with tracer.start_as_current_span("UserService.create") as span:
            span.set_attribute("email", email)

            user = await self.users.get_by_email(email)

            if user:
                logger.warning(
                    "user_creation_failed", reason="email_registered", email=email
                )
                raise EmailAlreadyRegistered(email=email)

            user = User(name=name, email=email)

            try:
                created = await self.users.create(user)
            except IntegrityError as exc:
                logger.warning("user_creation_failed", reason="email_registered", email=email)
                raise EmailAlreadyRegistered(email=email) from exc

            structlog.contextvars.bind_contextvars(user_id=created.id)
            span.set_attribute("user_id", created.id)
            logger.info("user_created", user_id=created.id, email=email)
            return created

    async def get_by_id(self, user_id: int) -> User:
        structlog.contextvars.bind_contextvars(user_id=user_id)

        with tracer.start_as_current_span("UserService.get_by_id") as span:
            span.set_attribute("user_id", user_id)

            user = await self.users.get_by_id(user_id)

            if not user:
                logger.warning("user_not_found", user_id=user_id)
                raise UserNotFound(user_id=user_id)

            return user

    async def get_loans(self, user_id: int) -> Sequence[Loan]:
        structlog.contextvars.bind_contextvars(user_id=user_id)

        with tracer.start_as_current_span("UserService.get_loans") as span:
            span.set_attribute("user_id", user_id)

            user = await self.users.get_by_id(user_id)

            if not user:
                logger.warning("user_not_found", user_id=user_id)
                raise UserNotFound(user_id=user_id)

            loans = await self.users.get_loans(user_id)
            span.set_attribute("loan_count", len(loans))
            return loans
