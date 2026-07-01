from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "sosed",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    timezone="UTC",
    task_track_started=True,
    beat_schedule={
        "cleanup-unverified-users-hourly": {
            "task": "app.workers.tasks.cleanup_unverified_users",
            "schedule": 3600.0,
        },
        "delete-old-posts-daily": {
            "task": "app.workers.tasks.delete_old_posts",
            "schedule": 86400.0,
        },
    },
)
