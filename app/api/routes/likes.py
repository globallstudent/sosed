import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.services import like_service

router = APIRouter(prefix="/posts/{post_id}/like", tags=["likes"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def like_post(post_id: uuid.UUID, db: DbSession, user: CurrentUser) -> dict[str, str]:
    await like_service.like_post(db, user, post_id)
    return {"detail": "Post liked"}


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(post_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    await like_service.unlike_post(db, user, post_id)
