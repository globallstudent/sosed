import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models import Post, User
from app.schemas import PostCreate, PostUpdate


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


async def get_post_or_404(db: AsyncSession, post_id: uuid.UUID) -> Post:
    post = await db.get(Post, post_id)
    if post is None:
        raise NotFoundError("Post not found")
    return post


def _ensure_author(post: Post, user: User) -> None:
    if post.author_id != user.id:
        raise PermissionDeniedError("You can only modify your own posts")


def build_posts_query(
    *,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> Select[tuple[Post]]:
    stmt = select(Post)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(or_(Post.title.ilike(pattern), Post.content.ilike(pattern)))
    if date_from:
        stmt = stmt.where(Post.created_at >= _as_utc(date_from))
    if date_to:
        stmt = stmt.where(Post.created_at <= _as_utc(date_to))

    return stmt.order_by(Post.created_at.desc())


async def create_post(db: AsyncSession, author: User, data: PostCreate) -> Post:
    post = Post(author_id=author.id, title=data.title, content=data.content)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post(
    db: AsyncSession, post_id: uuid.UUID, user: User, data: PostUpdate
) -> Post:
    post = await get_post_or_404(db, post_id)
    _ensure_author(post, user)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: uuid.UUID, user: User) -> None:
    post = await get_post_or_404(db, post_id)
    _ensure_author(post, user)
    await db.delete(post)
    await db.commit()
