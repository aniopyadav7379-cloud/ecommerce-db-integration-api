from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate


class InsufficientStockError(Exception):
    def __init__(self, product_id: int, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Product {product_id} has only {available} in stock, requested {requested}"
        )


class ProductNotFoundError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found")


def get_order(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def list_orders_for_user(db: Session, user_id: int) -> list[Order]:
    stmt = select(Order).where(Order.user_id == user_id)
    return list(db.execute(stmt).scalars().all())


def create_order(db: Session, payload: OrderCreate) -> Order:
    """
    Creates an order and its line items atomically.

    Data-handling rules enforced here (proper data handling, per Pillar 3):
      - Every product referenced must exist.
      - Stock must cover the requested quantity; stock is decremented.
      - price_at_purchase is snapshotted from the Product's current price,
        so later price changes never rewrite order history.
    All of this happens inside a single DB transaction: if any line item
    fails validation, nothing is committed.
    """
    order = Order(user_id=payload.user_id, status=OrderStatus.PENDING)

    for item in payload.items:
        product = db.get(Product, item.product_id)
        if product is None:
            db.rollback()
            raise ProductNotFoundError(item.product_id)
        if product.stock < item.quantity:
            db.rollback()
            raise InsufficientStockError(product.id, product.stock, item.quantity)

        product.stock -= item.quantity
        order.items.append(
            OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=product.price,
            )
        )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, db_order: Order, status: OrderStatus) -> Order:
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, db_order: Order) -> None:
    # Restores stock for cancelled/deleted orders so inventory stays accurate.
    for item in db_order.items:
        item.product.stock += item.quantity
    db.delete(db_order)
    db.commit()
