import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models import Comment, User
from app.schemas import CommentCreate
from app.services import post_service


async def list_for_post(db: AsyncSession, post_id: uuid.UUID) -> Sequence[Comment]:
    result = await db.scalars(
        select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at)
    )
    return result.all()


async def create_comment(
    db: AsyncSession, post_id: uuid.UUID, author: User, data: CommentCreate
) -> Comment:
    await post_service.get_post_or_404(db, post_id)

    comment = Comment(post_id=post_id, author_id=author.id, content=data.content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(
    db: AsyncSession, post_id: uuid.UUID, comment_id: uuid.UUID, user: User
) -> None:
    comment = await db.get(Comment, comment_id)
    if comment is None or comment.post_id != post_id:
        raise NotFoundError("Comment not found")
    if comment.author_id != user.id:
        raise PermissionDeniedError("You can only delete your own comments")

    await db.delete(comment)
    await db.commit()
