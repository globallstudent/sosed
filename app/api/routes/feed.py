from fastapi import APIRouter

from app.api.deps import DbSession, PaginationParams
from app.schemas.feed import FeedPost, FeedUser
from app.services import feed_service

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=list[FeedUser])
async def get_feed(db: DbSession, pagination: PaginationParams) -> list[FeedUser]:
    users = await feed_service.get_feed(db, pagination.limit, pagination.offset)
    return [
        FeedUser(
            username=user.username,
            posts=[
                FeedPost(
                    id=post.id,
                    title=post.title,
                    content=post.content,
                    likes=[like.user_id for like in post.likes],
                )
                for post in user.posts
            ],
        )
        for user in users
    ]
