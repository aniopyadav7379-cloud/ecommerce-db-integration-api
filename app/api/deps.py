from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.crud import user as user_crud, product as product_crud, order as order_crud

__all__ = ["get_db"]


def get_existing_user(user_id: int, db: Session = Depends(get_db)) -> User:
    db_user = user_crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


def get_existing_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    db_product = product_crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return db_product


def get_existing_order(order_id: int, db: Session = Depends(get_db)) -> Order:
    db_order = order_crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return db_order
