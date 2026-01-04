from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="RESTRICT"), nullable=False
    )

    due_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    loaned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    fine_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="loans", lazy="selectin")
    book = relationship("Book", back_populates="loans", lazy="selectin")

    __table_args__ = (
        Index(
            "uq_active_loan_per_book",
            "book_id",
            unique=True,
            postgresql_where=text("returned_at IS NULL"),
        ),
        Index(
            "idx_loan_active_due",
            "due_to",
            "id",
            postgresql_where=text("returned_at IS NULL"),
        ),
        CheckConstraint(
            "returned_at IS NULL OR returned_at >= loaned_at",
            name="ck_loan_returned_after_loaned",
        ),
    )
