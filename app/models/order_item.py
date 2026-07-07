from sqlalchemy import ForeignKey, Integer, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class OrderItem(Base):
    """
    Junction table between Order and Product (Many-to-Many).
    Storing quantity and price_at_purchase here (rather than only IDs)
    is what makes this a "dedicated intermediary table" instead of a
    bare association table -- it preserves historical pricing even if
    the Product's price changes later.
    """

    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("price_at_purchase >= 0", name="ck_order_items_price_non_negative"),
        # A product should only appear once per order; increase quantity instead
        # of adding a duplicate row.
        UniqueConstraint("order_id", "product_id", name="uq_order_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
