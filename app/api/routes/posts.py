import uuid

from fastapi import APIRouter, status

from app.api.deps import DbSession, PaginationParams, PostFilterParams, VerifiedUser
from app.schemas import CommentOut, PostCreate, PostDetailOut, PostOut, PostUpdate
from app.services import comment_service, post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostOut])
async def list_posts(
    db: DbSession, pagination: PaginationParams, filters: PostFilterParams
) -> list[PostOut]:
    return await post_service.list_posts(
        db,
        limit=pagination.limit,
        offset=pagination.offset,
        search=filters.search,
        date_from=filters.date_from,
        date_to=filters.date_to,
    )


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, db: DbSession, user: VerifiedUser) -> PostOut:
    return await post_service.create_post(db, user, data)


@router.get("/{post_id}", response_model=PostDetailOut)
async def get_post(post_id: uuid.UUID, db: DbSession) -> PostDetailOut:
    post = await post_service.get_post_or_404(db, post_id)
    comments = await comment_service.list_for_post(db, post_id)
    detail = PostDetailOut.model_validate(post)
    detail.comments = [CommentOut.model_validate(c) for c in comments]
    return detail


@router.patch("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: uuid.UUID, data: PostUpdate, db: DbSession, user: VerifiedUser
) -> PostOut:
    return await post_service.update_post(db, post_id, user, data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: uuid.UUID, db: DbSession, user: VerifiedUser) -> None:
    await post_service.delete_post(db, post_id, user)
