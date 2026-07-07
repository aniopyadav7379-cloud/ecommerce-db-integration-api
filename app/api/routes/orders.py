from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_existing_order
from app.crud import order as order_crud
from app.crud.order import InsufficientStockError, ProductNotFoundError
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    try:
        return order_crud.create_order(db, payload)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{order_id}", response_model=OrderRead)
def read_order(db_order: Order = Depends(get_existing_order)):
    return db_order


@router.get("/user/{user_id}", response_model=list[OrderRead])
def list_orders_for_user(user_id: int, db: Session = Depends(get_db)):
    return order_crud.list_orders_for_user(db, user_id)


@router.put("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    payload: OrderStatusUpdate,
    db_order: Order = Depends(get_existing_order),
    db: Session = Depends(get_db),
):
    return order_crud.update_order_status(db, db_order, payload.status)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(db_order: Order = Depends(get_existing_order), db: Session = Depends(get_db)):
    order_crud.delete_order(db, db_order)
    return None
