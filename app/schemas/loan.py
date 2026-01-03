from datetime import datetime

from app.schemas.wire import WireModel


class LoanCreate(WireModel):
    user_id: int
    book_id: int


class LoanResponse(WireModel):
    id: int
    book_id: int
    user_id: int
    loaned_at: datetime
    due_to: datetime
    returned_at: datetime | None
    fine_cents: int
