from fastapi import APIRouter, status

from app.api.dependencies import book_service
from app.schemas.book import BookCreate, BookResponse
from app.services.book import BookService

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
async def list_books(
    offset: int = 0, limit: int = 50, books: BookService = book_service()
):
    return await books.list_all(offset=offset, limit=limit)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, books: BookService = book_service()):
    return await books.get_by_id(book_id=book_id)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, books: BookService = book_service()):
    return await books.create(title=book.title, author=book.author)
