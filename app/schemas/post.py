import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.comment import CommentOut


class PostCreate(BaseModel):
    title: str = Field(min_length=5, max_length=255)
    content: str = Field(min_length=1, max_length=10_000)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    content: str | None = Field(default=None, min_length=1, max_length=10_000)


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class PostDetailOut(PostOut):
    comments: list[CommentOut] = Field(default_factory=list)
