from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from app.models import Post, User


def build_feed_query() -> Select[tuple[User]]:
    return (
        select(User)
        .options(selectinload(User.posts).selectinload(Post.likes))
        .order_by(User.created_at)
    )
