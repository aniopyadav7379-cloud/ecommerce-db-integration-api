from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_existing_product
from app.crud import product as product_crud
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return product_crud.create_product(db, payload)


@router.get("", response_model=list[ProductRead])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_crud.list_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def read_product(db_product: Product = Depends(get_existing_product)):
    return db_product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    payload: ProductUpdate,
    db_product: Product = Depends(get_existing_product),
    db: Session = Depends(get_db),
):
    return product_crud.update_product(db, db_product, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(db_product: Product = Depends(get_existing_product), db: Session = Depends(get_db)):
    product_crud.delete_product(db, db_product)
    return None
