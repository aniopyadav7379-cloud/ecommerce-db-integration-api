from sqlalchemy import String, Numeric, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Product(Base):
    """
    Catalog item.
    Relationship: Many-to-Many with Order, through the OrderItem junction table.
    """

    __tablename__ = "products"
    __table_args__ = (
        # CHECK constraints: the database enforces valid values regardless
        # of what the application layer sends.
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        CheckConstraint("stock >= 0", name="ck_products_stock_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
