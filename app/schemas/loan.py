from datetime import datetime
from pydantic import BaseModel


class LoanCreate(BaseModel):
    user_id: int
    book_id: int

    class Config:
        from_attributes = True


class LoanResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    loaned_at: datetime
    due_to: datetime
    returned_at: datetime | None
    fine_cents: int

    class Config:
        from_attributes = True
