from pydantic import EmailStr

from app.schemas.wire import WireModel


class UserCreate(WireModel):
    name: str
    email: EmailStr


class UserResponse(WireModel):
    id: int
    name: str
    email: EmailStr
