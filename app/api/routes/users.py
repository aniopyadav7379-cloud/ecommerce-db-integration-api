from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_existing_user
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """CREATE = POST = SQL INSERT."""
    if user_crud.get_user_by_email(db, payload.email) is not None:
        # The UNIQUE constraint on users.email would also catch this at the
        # DB level; checking here gives a friendlier 409 instead of a 500.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return user_crud.create_user(db, payload)


@router.get("", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """READ (collection) = GET = SQL SELECT."""
    return user_crud.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def read_user(db_user: User = Depends(get_existing_user)):
    """READ (single) = GET = SQL SELECT."""
    return db_user


@router.put("/{user_id}", response_model=UserRead)
def update_user(payload: UserUpdate, db_user: User = Depends(get_existing_user), db: Session = Depends(get_db)):
    """UPDATE = PUT = SQL UPDATE."""
    return user_crud.update_user(db, db_user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db_user: User = Depends(get_existing_user), db: Session = Depends(get_db)):
    """DELETE = DELETE = SQL DELETE."""
    user_crud.delete_user(db, db_user)
    return None
