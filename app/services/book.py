from collections.abc import Sequence

import structlog
from opentelemetry import trace

from app.db.models.book import Book
from app.exceptions.domain import BookNotFound
from app.repositories.book import BookRepository

logger = structlog.get_logger("sgbd.services.book")
tracer = trace.get_tracer("sgbd.services.book")


class BookService:
    def __init__(self, books: BookRepository):
        self.books = books

    async def list_all(self, *, offset: int = 0, limit: int = 50) -> Sequence[Book]:
        with tracer.start_as_current_span("BookService.list_all") as span:
            span.set_attribute("offset", offset)
            span.set_attribute("limit", limit)
            books = await self.books.list_all(offset=offset, limit=limit)
            span.set_attribute("result_count", len(books))
            return books

    async def get_by_id(self, *, book_id: int) -> Book:
        structlog.contextvars.bind_contextvars(book_id=book_id)

        with tracer.start_as_current_span("BookService.get_by_id") as span:
            span.set_attribute("book_id", book_id)

            book = await self.books.get_by_id(book_id)

            if book is None:
                logger.warning("book_not_found", book_id=book_id)
                raise BookNotFound(book_id=book_id)

            return book

    async def create(self, *, title: str, author: str) -> Book:
        with tracer.start_as_current_span("BookService.create") as span:
            span.set_attribute("title", title)
            span.set_attribute("author", author)

            book = Book(title=title, author=author)
            created = await self.books.create(book)

            structlog.contextvars.bind_contextvars(book_id=created.id)
            span.set_attribute("book_id", created.id)
            logger.info("book_created", book_id=created.id, title=title)
            return created
