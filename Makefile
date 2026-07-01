.PHONY: dev celery-worker celery-beat migrate lint

dev:
	uv run uvicorn app.main:app --reload

celery-worker:
	uv run celery -A app.workers.celery_app:celery_app worker --loglevel=info

celery-beat:
	uv run celery -A app.workers.celery_app:celery_app beat --loglevel=info

migrate:
	uv run alembic upgrade head

lint:
	uv run ruff check app
