from collections.abc import Sequence

from fastapi import APIRouter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.api.deps import DbSession
from app.models import User
from app.schemas.feed import FeedPost, FeedUser
from app.services import feed_service

router = APIRouter(tags=["feed"])


def _to_feed_users(users: Sequence[User]) -> list[FeedUser]:
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


@router.get("/feed")
async def get_feed(db: DbSession) -> Page[FeedUser]:
    return await paginate(db, feed_service.build_feed_query(), transformer=_to_feed_users)
