from app.schemas.wire import WireModel


class BookCreate(WireModel):
    title: str
    author: str


class BookResponse(WireModel):
    id: int
    title: str
    author: str
