from collections.abc import Sequence

import structlog
from opentelemetry import trace
from sqlalchemy.exc import IntegrityError

from app.cache.book import BookCache
from app.db.models.book import Book
from app.db.models.book_copy import BookCopy
from app.exceptions.domain import BookAlreadyExists, BookNotFound
from app.repositories.book import BookRepository
from app.repositories.book_copy import BookCopyRepository

logger = structlog.get_logger("sgbd.services.book")
tracer = trace.get_tracer("sgbd.services.book")


class BookService:
    def __init__(
        self, books: BookRepository, copies: BookCopyRepository, cache: BookCache
    ):
        self.books = books
        self.copies = copies
        self.cache = cache

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

            # Try cache first
            book = await self.cache.get(book_id)
            if book is not None:
                span.set_attribute("cache_hit", True)
                return book

            span.set_attribute("cache_hit", False)
            book = await self.books.get_by_id(book_id)

            if book is None:
                logger.warning("book_not_found", book_id=book_id)
                raise BookNotFound(book_id=book_id)

            # Populate cache on DB hit
            await self.cache.set(book)
            return book

    async def create(self, *, title: str, author: str) -> Book:
        with tracer.start_as_current_span("BookService.create") as span:
            span.set_attribute("title", title)
            span.set_attribute("author", author)

            book = Book(title=title, author=author)

            try:
                created = await self.books.create(book)
            except IntegrityError as exc:
                logger.warning(
                    "book_creation_failed",
                    reason="book_already_exists",
                    title=title,
                    author=author,
                )
                raise BookAlreadyExists(title=title, author=author) from exc

            structlog.contextvars.bind_contextvars(book_id=created.id)
            span.set_attribute("book_id", created.id)
            logger.info("book_created", book_id=created.id, title=title)
            return created

    async def create_copy(self, *, book_id: int) -> BookCopy:
        with tracer.start_as_current_span("BookService.create_copy") as span:
            span.set_attribute("book_id", book_id)

            if not await self.books.exists(book_id):
                logger.warning("copy_creation_failed", reason="book_not_found")
                raise BookNotFound(book_id=book_id)

            copy = BookCopy(book_id=book_id)
            created = await self.copies.create(copy)

            span.set_attribute("copy_id", created.id)
            logger.info("copy_created", book_id=book_id, copy_id=created.id)
            return created

    async def list_copies(self, *, book_id: int) -> Sequence[BookCopy]:
        with tracer.start_as_current_span("BookService.list_copies") as span:
            span.set_attribute("book_id", book_id)

            if not await self.books.exists(book_id):
                logger.warning("list_copies_failed", reason="book_not_found")
                raise BookNotFound(book_id=book_id)

            copies = await self.copies.list_by_book(book_id)
            span.set_attribute("copy_count", len(copies))
            return copies
