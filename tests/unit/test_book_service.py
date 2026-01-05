from unittest.mock import AsyncMock

import pytest

from app.db.models.book import Book
from app.exceptions.domain import BookNotFound
from app.services.book import BookService


@pytest.fixture
def mock_book_repo():
    return AsyncMock()


@pytest.fixture
def mock_book_cache():
    cache = AsyncMock()
    cache.get.return_value = None  # Default: cache miss
    return cache


@pytest.fixture
def book_service(mock_book_repo, mock_book_cache):
    return BookService(books=mock_book_repo, cache=mock_book_cache)


class TestBookServiceCreate:
    async def test_create_success(self, book_service, mock_book_repo):
        mock_book_repo.create.return_value = Book(
            id=1, title="Dom Casmurro", author="Machado de Assis"
        )

        result = await book_service.create(
            title="Dom Casmurro", author="Machado de Assis"
        )

        assert result.id == 1
        assert result.title == "Dom Casmurro"
        assert result.author == "Machado de Assis"
        mock_book_repo.create.assert_called_once()


class TestBookServiceGetById:
    async def test_get_by_id_success(self, book_service, mock_book_repo):
        mock_book_repo.get_by_id.return_value = Book(
            id=1, title="Dom Casmurro", author="Machado de Assis"
        )

        result = await book_service.get_by_id(book_id=1)

        assert result.id == 1
        assert result.title == "Dom Casmurro"
        mock_book_repo.get_by_id.assert_called_once_with(1)

    async def test_get_by_id_not_found(self, book_service, mock_book_repo):
        mock_book_repo.get_by_id.return_value = None

        with pytest.raises(BookNotFound) as exc_info:
            await book_service.get_by_id(book_id=999)

        assert exc_info.value.context["book_id"] == 999


class TestBookServiceListAll:
    async def test_list_all(self, book_service, mock_book_repo):
        mock_book_repo.list_all.return_value = [
            Book(id=1, title="Book 1", author="Author 1"),
            Book(id=2, title="Book 2", author="Author 2"),
        ]

        result = await book_service.list_all(offset=0, limit=10)

        assert len(result) == 2
        mock_book_repo.list_all.assert_called_once_with(offset=0, limit=10)

    async def test_list_all_empty(self, book_service, mock_book_repo):
        mock_book_repo.list_all.return_value = []

        result = await book_service.list_all(offset=0, limit=10)

        assert len(result) == 0

    async def test_list_all_with_pagination(self, book_service, mock_book_repo):
        mock_book_repo.list_all.return_value = [
            Book(id=3, title="Book 3", author="Author 3")
        ]

        result = await book_service.list_all(offset=2, limit=1)

        assert len(result) == 1
        mock_book_repo.list_all.assert_called_once_with(offset=2, limit=1)
