from datetime import datetime

from app.schemas.wire import WireModel


class BookCopyCreate(WireModel):
    book_id: int


class BookCopyResponse(WireModel):
    id: int
    book_id: int
    acquired_at: datetime
