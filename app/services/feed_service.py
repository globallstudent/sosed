from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Post, User


async def get_feed(db: AsyncSession, limit: int, offset: int) -> Sequence[User]:
    stmt = (
        select(User)
        .options(selectinload(User.posts).selectinload(Post.likes))
        .order_by(User.created_at)
        .limit(limit)
        .offset(offset)
    )
    return (await db.scalars(stmt)).all()
