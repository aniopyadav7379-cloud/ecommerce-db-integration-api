from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserProfile(Base):
    """
    Extended profile data kept separate from the core `users` table.
    The UNIQUE constraint on user_id is what makes this relationship
    strictly One-to-One rather than One-to-Many.
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # unique=True is the key constraint that enforces 1:1 instead of 1:Many.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address_line: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
