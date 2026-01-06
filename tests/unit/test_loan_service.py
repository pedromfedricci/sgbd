from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models.book_copy import BookCopy
from app.db.models.loan import Loan
from app.db.models.user import User
from app.exceptions.domain import (
    BookNotFound,
    LoanAlreadyReturned,
    LoanNotFound,
    MaxActiveLoansExceeded,
    NoCopiesAvailable,
    UserNotFound,
)
from app.services.loan import (
    DAILY_FINE_CENTS,
    LOAN_DAYS,
    MAX_ACTIVE_LOANS,
    LoanService,
)

USER_1: User = User(id=1, name="Test", email="test@email.com")
COPY_1: BookCopy = BookCopy(id=1, book_id=1)


@pytest.fixture
def mock_repos():
    return {
        "loans": AsyncMock(),
        "users": AsyncMock(),
        "books": AsyncMock(),
        "copies": AsyncMock(),
    }


@pytest.fixture
def loan_service(mock_repos):
    return LoanService(
        loans=mock_repos["loans"],
        users=mock_repos["users"],
        books=mock_repos["books"],
        copies=mock_repos["copies"],
    )


class TestLoanServiceCreate:
    async def test_create_success(self, loan_service, mock_repos):
        mock_repos["books"].exists.return_value = True
        mock_repos["users"].get_for_update.return_value = USER_1
        mock_repos["loans"].count_active_by_user.return_value = 0
        mock_repos["copies"].get_available_for_book.return_value = COPY_1
        mock_repos["loans"].save.return_value = Loan(
            id=1,
            user_id=1,
            copy_id=1,
            due_to=datetime.now(UTC) + timedelta(days=LOAN_DAYS),
        )

        result = await loan_service.create(user_id=1, book_id=1)

        assert result.id == 1
        assert result.user_id == 1
        assert result.copy_id == 1
        mock_repos["books"].exists.assert_called_once_with(1)
        mock_repos["users"].get_for_update.assert_called_once_with(1)
        mock_repos["loans"].count_active_by_user.assert_called_once_with(1)
        mock_repos["copies"].get_available_for_book.assert_called_once_with(1)
        mock_repos["loans"].save.assert_called_once()

    async def test_create_user_not_found(self, loan_service, mock_repos):
        mock_repos["books"].exists.return_value = True
        mock_repos["users"].get_for_update.return_value = None

        with pytest.raises(UserNotFound) as exc_info:
            await loan_service.create(user_id=999, book_id=1)

        assert exc_info.value.context["user_id"] == 999
        mock_repos["loans"].save.assert_not_called()

    async def test_create_book_not_found(self, loan_service, mock_repos):
        mock_repos["books"].exists.return_value = False

        with pytest.raises(BookNotFound) as exc_info:
            await loan_service.create(user_id=1, book_id=999)

        assert exc_info.value.context["book_id"] == 999
        mock_repos["users"].get_for_update.assert_not_called()
        mock_repos["loans"].save.assert_not_called()

    async def test_create_max_loans_exceeded(self, loan_service, mock_repos):
        mock_repos["books"].exists.return_value = True
        mock_repos["users"].get_for_update.return_value = USER_1
        mock_repos["loans"].count_active_by_user.return_value = MAX_ACTIVE_LOANS

        with pytest.raises(MaxActiveLoansExceeded) as exc_info:
            await loan_service.create(user_id=1, book_id=1)

        assert exc_info.value.context["user_id"] == 1
        assert exc_info.value.context["active"] == MAX_ACTIVE_LOANS
        mock_repos["loans"].save.assert_not_called()

    async def test_create_no_copies_available(self, loan_service, mock_repos):
        mock_repos["books"].exists.return_value = True
        mock_repos["users"].get_for_update.return_value = USER_1
        mock_repos["loans"].count_active_by_user.return_value = 0
        mock_repos["copies"].get_available_for_book.return_value = None

        with pytest.raises(NoCopiesAvailable) as exc_info:
            await loan_service.create(user_id=1, book_id=1)

        assert exc_info.value.context["book_id"] == 1
        mock_repos["loans"].save.assert_not_called()

    async def test_create_concurrent_copy_taken(self, loan_service, mock_repos):
        mock_repos["books"].exists.return_value = True
        mock_repos["users"].get_for_update.return_value = USER_1
        mock_repos["loans"].count_active_by_user.return_value = 0
        mock_repos["copies"].get_available_for_book.return_value = COPY_1
        mock_repos["loans"].save.side_effect = IntegrityError(None, None, Exception())

        with pytest.raises(NoCopiesAvailable) as exc_info:
            await loan_service.create(user_id=1, book_id=1)

        assert exc_info.value.context["book_id"] == 1


class TestLoanServiceFulfill:
    async def test_fulfill_on_time(self, loan_service, mock_repos):
        due_date = datetime.now(UTC) + timedelta(days=7)
        loan = Loan(
            id=1, user_id=1, copy_id=1, due_to=due_date, returned_at=None, fine_cents=0
        )
        mock_repos["loans"].get_by_id.return_value = loan
        mock_repos["loans"].save.return_value = loan

        result = await loan_service.fulfill(loan_id=1)

        assert result.returned_at is not None
        assert result.fine_cents == 0
        mock_repos["loans"].get_by_id.assert_called_once_with(1)

    async def test_fulfill_late_with_fine(self, loan_service, mock_repos):
        days_late = 5
        due_date = datetime.now(UTC) - timedelta(days=days_late)
        loan = Loan(
            id=1, user_id=1, copy_id=1, due_to=due_date, returned_at=None, fine_cents=0
        )
        mock_repos["loans"].get_by_id.return_value = loan
        mock_repos["loans"].save.return_value = loan

        result = await loan_service.fulfill(loan_id=1)

        assert result.returned_at is not None
        assert result.fine_cents == days_late * DAILY_FINE_CENTS

    async def test_fulfill_not_found(self, loan_service, mock_repos):
        mock_repos["loans"].get_by_id.return_value = None

        with pytest.raises(LoanNotFound) as exc_info:
            await loan_service.fulfill(loan_id=999)

        assert exc_info.value.context["loan_id"] == 999

    async def test_fulfill_already_returned(self, loan_service, mock_repos):
        loan = Loan(
            id=1,
            user_id=1,
            copy_id=1,
            due_to=datetime.now(UTC),
            returned_at=datetime.now(UTC),
            fine_cents=0,
        )
        mock_repos["loans"].get_by_id.return_value = loan

        with pytest.raises(LoanAlreadyReturned) as exc_info:
            await loan_service.fulfill(loan_id=1)

        assert exc_info.value.context["loan_id"] == 1


class TestLoanServiceListByUser:
    async def test_list_by_user_success(self, loan_service, mock_repos):
        mock_repos["users"].exists.return_value = True
        mock_repos["loans"].list_by_user.return_value = [
            Loan(id=1, user_id=1, copy_id=1),
            Loan(id=2, user_id=1, copy_id=2),
        ]

        result = await loan_service.list_by_user(user_id=1)

        assert len(result) == 2
        mock_repos["users"].exists.assert_called_once_with(1)
        mock_repos["loans"].list_by_user.assert_called_once_with(1)

    async def test_list_by_user_not_found(self, loan_service, mock_repos):
        mock_repos["users"].exists.return_value = False

        with pytest.raises(UserNotFound):
            await loan_service.list_by_user(user_id=999)

        mock_repos["loans"].list_by_user.assert_not_called()


class TestLoanServiceListActive:
    async def test_list_active(self, loan_service, mock_repos):
        mock_repos["loans"].list_active.return_value = [
            Loan(id=1, user_id=1, copy_id=1),
        ]

        result = await loan_service.list_active(offset=0, limit=10)

        assert len(result) == 1
        mock_repos["loans"].list_active.assert_called_once_with(offset=0, limit=10)


class TestLoanServiceListOverdue:
    async def test_list_overdue(self, loan_service, mock_repos):
        mock_repos["loans"].list_overdue.return_value = [
            Loan(id=1, user_id=1, copy_id=1),
        ]

        result = await loan_service.list_overdue(offset=0, limit=10)

        assert len(result) == 1
        mock_repos["loans"].list_overdue.assert_called_once_with(offset=0, limit=10)
