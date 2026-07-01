import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

import jwt
from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User
from app.services import user_service

DbSession = Annotated[AsyncSession, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False)
BearerToken = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


async def get_current_user(db: DbSession, credentials: BearerToken) -> User:
    if credentials is None:
        raise AuthenticationError()

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise AuthenticationError() from exc

    user = await user_service.get_by_id(db, user_id)
    if user is None:
        raise AuthenticationError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_verified_user(current_user: CurrentUser) -> User:
    if not current_user.is_verified:
        raise PermissionDeniedError("Email verification required")
    return current_user


VerifiedUser = Annotated[User, Depends(get_current_verified_user)]


@dataclass
class PostFilters:
    search: str | None
    date_from: datetime | None
    date_to: datetime | None


def get_post_filters(
    search: Annotated[str | None, Query(max_length=255)] = None,
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
) -> PostFilters:
    return PostFilters(search=search, date_from=date_from, date_to=date_to)


PostFilterParams = Annotated[PostFilters, Depends(get_post_filters)]
