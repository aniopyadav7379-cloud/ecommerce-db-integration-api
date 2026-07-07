from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus
from app.schemas.product import ProductRead


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderItemRead(BaseModel):
    id: int
    product: ProductRead
    quantity: int
    price_at_purchase: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderRead(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    items: list[OrderItemRead]
    model_config = ConfigDict(from_attributes=True)
