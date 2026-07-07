from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int) -> User | None:
    # SQLAlchemy's ORM layer always binds parameters -- this never
    # concatenates user input into raw SQL, so it is immune to injection.
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    stmt = select(User).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def create_user(db: Session, payload: UserCreate) -> User:
    db_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=pwd_context.hash(payload.password),
    )
    if payload.profile is not None:
        db_user.profile = UserProfile(**payload.profile.model_dump())

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, payload: UserUpdate) -> User:
    if payload.full_name is not None:
        db_user.full_name = payload.full_name
    if payload.password is not None:
        db_user.hashed_password = pwd_context.hash(payload.password)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User) -> None:
    db.delete(db_user)
    db.commit()
