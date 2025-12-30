from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str


class BookResponse(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        from_attributes = True

