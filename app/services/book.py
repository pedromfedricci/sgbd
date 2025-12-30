from app.db.models.book import Book
from app.repositories.book import BookRepository
from app.exceptions.domain import BookNotFound

from typing import Sequence


class BookService:
    def __init__(self, books: BookRepository):
        self.books = books

    async def list_all(self, *, offset: int = 0, limit: int = 50) -> Sequence[Book]:
        return await self.books.list(offset=offset, limit=limit)

    async def get_by_id(self, book_id: int) -> Book:
        book = await self.books.get_by_id(book_id)

        if book is None:
            raise BookNotFound(book_id=book_id)

        return book

    async def create(self, *, title: str, author: str) -> Book:
        book = Book(title=title, author=author)
        return await self.books.add(book)
