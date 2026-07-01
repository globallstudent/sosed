from fastapi import APIRouter, status

from app.workers.tasks import cleanup_unverified_users

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/cleanup-unverified", status_code=status.HTTP_202_ACCEPTED)
async def trigger_cleanup() -> dict[str, str]:
    task = cleanup_unverified_users.delay()
    return {"task_id": task.id}
