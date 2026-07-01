import logging
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import BadRequestError
from app.models import EmailVerificationToken, User

logger = logging.getLogger(__name__)
settings = get_settings()


async def issue_token(db: AsyncSession, user: User) -> EmailVerificationToken:
    token = EmailVerificationToken(
        user_id=user.id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(UTC) + timedelta(hours=settings.email_verification_expire_hours),
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)

    _enqueue_verification_email(user.email, token.token)
    return token


def _enqueue_verification_email(email: str, token_value: str) -> None:
    from app.workers.tasks import send_verification_email

    try:
        send_verification_email.delay(email, token_value)
    except Exception:
        logger.exception("Failed to enqueue verification email for %s", email)


async def verify_email(db: AsyncSession, token_value: str) -> User:
    record = await db.scalar(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token_value)
    )
    if record is None or record.used_at is not None:
        raise BadRequestError("Invalid or already used verification token")
    if record.expires_at < datetime.now(UTC):
        raise BadRequestError("Verification token has expired")

    user = await db.get(User, record.user_id)
    user.is_verified = True
    record.used_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(user)
    return user
