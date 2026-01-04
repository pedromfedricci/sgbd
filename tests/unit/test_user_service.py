from unittest.mock import AsyncMock

import pytest

from app.db.models.loan import Loan
from app.db.models.user import User
from app.exceptions.domain import EmailAlreadyRegistered, UserNotFound
from app.services.user import UserService


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def user_service(mock_user_repo):
    return UserService(users=mock_user_repo)


class TestUserServiceCreate:
    async def test_create_success(self, user_service, mock_user_repo):
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = User(
            id=1, name="Test", email="test@email.com"
        )

        result = await user_service.create(name="Test", email="test@email.com")

        assert result.id == 1
        assert result.name == "Test"
        assert result.email == "test@email.com"
        mock_user_repo.get_by_email.assert_called_once_with("test@email.com")
        mock_user_repo.create.assert_called_once()

    async def test_create_email_already_registered(self, user_service, mock_user_repo):
        mock_user_repo.get_by_email.return_value = User(
            id=1, name="Existing", email="test@email.com"
        )

        with pytest.raises(EmailAlreadyRegistered) as exc_info:
            await user_service.create(name="Test", email="test@email.com")

        assert exc_info.value.context["email"] == "test@email.com"
        mock_user_repo.create.assert_not_called()


class TestUserServiceGetById:
    async def test_get_by_id_success(self, user_service, mock_user_repo):
        mock_user_repo.get_by_id.return_value = User(
            id=1, name="Test", email="test@email.com"
        )

        result = await user_service.get_by_id(1)

        assert result.id == 1
        mock_user_repo.get_by_id.assert_called_once_with(1)

    async def test_get_by_id_not_found(self, user_service, mock_user_repo):
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound) as exc_info:
            await user_service.get_by_id(999)

        assert exc_info.value.context["user_id"] == 999


class TestUserServiceListAll:
    async def test_list_all(self, user_service, mock_user_repo):
        mock_user_repo.list.return_value = [
            User(id=1, name="User 1", email="user1@email.com"),
            User(id=2, name="User 2", email="user2@email.com"),
        ]

        result = await user_service.list_all(offset=0, limit=10)

        assert len(result) == 2
        mock_user_repo.list.assert_called_once_with(offset=0, limit=10)

    async def test_list_all_empty(self, user_service, mock_user_repo):
        mock_user_repo.list.return_value = []

        result = await user_service.list_all(offset=0, limit=10)

        assert len(result) == 0


class TestUserServiceGetLoans:
    async def test_get_loans_success(self, user_service, mock_user_repo):
        mock_user_repo.get_by_id.return_value = User(
            id=1, name="Test", email="test@email.com"
        )
        mock_user_repo.get_loans.return_value = [
            Loan(id=1, user_id=1, book_id=1),
            Loan(id=2, user_id=1, book_id=2),
        ]

        result = await user_service.get_loans(1)

        assert len(result) == 2
        mock_user_repo.get_loans.assert_called_once_with(1)

    async def test_get_loans_user_not_found(self, user_service, mock_user_repo):
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await user_service.get_loans(999)

        mock_user_repo.get_loans.assert_not_called()
