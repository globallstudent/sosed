import uuid

from fastapi import APIRouter, status

from app.api.deps import DbSession, VerifiedUser
from app.schemas import CommentCreate, CommentOut
from app.services import comment_service

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.get("", response_model=list[CommentOut])
async def list_comments(post_id: uuid.UUID, db: DbSession) -> list[CommentOut]:
    return await comment_service.list_for_post(db, post_id)


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: uuid.UUID, data: CommentCreate, db: DbSession, user: VerifiedUser
) -> CommentOut:
    return await comment_service.create_comment(db, post_id, user, data)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: uuid.UUID, comment_id: uuid.UUID, db: DbSession, user: VerifiedUser
) -> None:
    await comment_service.delete_comment(db, post_id, comment_id, user)
