from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import verify_password
from app.models import User
from app.services import user_service


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    user = await user_service.get_by_email(db, email.lower())
    if user is None or not verify_password(password, user.password_hash):
        raise AuthenticationError("Incorrect email or password")
    return user
