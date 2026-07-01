import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.models import User
from app.schemas import UserCreate, UserUpdate


async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email))


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    return await db.scalar(select(User).where(User.username == username))


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    email = data.email.lower()
    if await get_by_email(db, email):
        raise ConflictError("Email already registered")
    if await get_by_username(db, data.username):
        raise ConflictError("Username already taken")

    user = User(
        email=email,
        username=data.username,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Email or username already exists") from exc
    await db.refresh(user)
    return user


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    updates = data.model_dump(exclude_unset=True)

    new_username = updates.get("username")
    if new_username and new_username != user.username and await get_by_username(db, new_username):
        raise ConflictError("Username already taken")

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Username already taken") from exc
    await db.refresh(user)
    return user
