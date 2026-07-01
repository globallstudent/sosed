import logging
import smtplib
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage

from sqlalchemy import delete

from app.core.config import get_settings
from app.db.sync_session import SyncSessionLocal
from app.models import Post, User
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.workers.tasks.cleanup_unverified_users")
def cleanup_unverified_users() -> int:
    cutoff = datetime.now(UTC) - timedelta(hours=settings.unverified_user_retention_hours)
    with SyncSessionLocal() as session:
        result = session.execute(
            delete(User).where(User.is_verified.is_(False), User.created_at < cutoff)
        )
        session.commit()
        deleted = result.rowcount

    logger.info("Deleted %s unverified users created before %s", deleted, cutoff.isoformat())
    return deleted


@celery_app.task(name="app.workers.tasks.delete_old_posts")
def delete_old_posts() -> int:
    if settings.post_retention_days <= 0:
        return 0

    cutoff = datetime.now(UTC) - timedelta(days=settings.post_retention_days)
    with SyncSessionLocal() as session:
        result = session.execute(delete(Post).where(Post.created_at < cutoff))
        session.commit()
        deleted = result.rowcount

    logger.info("Deleted %s posts created before %s", deleted, cutoff.isoformat())
    return deleted


@celery_app.task(
    name="app.workers.tasks.send_verification_email",
    autoretry_for=(OSError,),
    retry_backoff=True,
    max_retries=3,
)
def send_verification_email(email: str, token: str) -> None:
    link = f"{settings.app_base_url}/auth/verify-email?token={token}"

    message = EmailMessage()
    message["Subject"] = "Confirm your Sosed account"
    message["From"] = settings.smtp_from
    message["To"] = email
    message.set_content(f"Welcome to Sosed!\n\nConfirm your email:\n{link}\n")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)

    logger.info("Sent verification email to %s", email)
