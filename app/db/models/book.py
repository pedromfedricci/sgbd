from app.db.base import Base

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.indexable import index_property


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")

    index_property("title", "ix_book_title")

    __table_args__ = (Index("ix_book_title", "title"),)
