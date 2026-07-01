from fastapi import APIRouter, Request, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.exceptions import BadRequestError
from app.core.limiter import limiter
from app.core.security import create_access_token
from app.schemas import LoginRequest, Token, UserCreate, UserOut
from app.services import auth_service, user_service, verification_service

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: DbSession) -> UserOut:
    user = await user_service.create_user(db, data)
    await verification_service.issue_token(db, user)
    return user


@router.post("/login", response_model=Token)
@limiter.limit(settings.login_rate_limit)
async def login(request: Request, data: LoginRequest, db: DbSession) -> Token:
    user = await auth_service.authenticate(db, data.email, data.password)
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser) -> UserOut:
    return current_user


@router.get("/verify-email")
async def verify_email(token: str, db: DbSession) -> dict[str, str]:
    await verification_service.verify_email(db, token)
    return {"detail": "Email verified"}


@router.post("/request-verification", status_code=status.HTTP_202_ACCEPTED)
async def request_verification(current_user: CurrentUser, db: DbSession) -> dict[str, str]:
    if current_user.is_verified:
        raise BadRequestError("Email already verified")
    await verification_service.issue_token(db, current_user)
    return {"detail": "Verification email sent"}
