import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.models import Like, User
from app.services import post_service


async def like_post(db: AsyncSession, user: User, post_id: uuid.UUID) -> None:
    post = await post_service.get_post_or_404(db, post_id)
    if post.author_id == user.id:
        raise PermissionDeniedError("You cannot like your own post")

    db.add(Like(user_id=user.id, post_id=post_id))
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Post already liked") from exc


async def unlike_post(db: AsyncSession, user: User, post_id: uuid.UUID) -> None:
    like = await db.get(Like, {"user_id": user.id, "post_id": post_id})
    if like is None:
        raise NotFoundError("Like not found")
    await db.delete(like)
    await db.commit()
