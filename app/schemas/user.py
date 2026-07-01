import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$"
FULL_NAME_PATTERN = r"^[A-Za-zА-Яа-яЁё \-]+$"


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32, pattern=USERNAME_PATTERN)
    full_name: str = Field(min_length=2, max_length=100, pattern=FULL_NAME_PATTERN)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None, min_length=3, max_length=32, pattern=USERNAME_PATTERN
    )
    full_name: str | None = Field(
        default=None, min_length=2, max_length=100, pattern=FULL_NAME_PATTERN
    )


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime
