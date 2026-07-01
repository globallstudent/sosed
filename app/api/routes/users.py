from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas import UserOut, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=UserOut)
async def update_me(data: UserUpdate, db: DbSession, current_user: CurrentUser) -> UserOut:
    return await user_service.update_profile(db, current_user, data)
