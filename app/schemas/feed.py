import uuid

from pydantic import BaseModel


class FeedPost(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    likes: list[uuid.UUID]


class FeedUser(BaseModel):
    username: str
    posts: list[FeedPost]
