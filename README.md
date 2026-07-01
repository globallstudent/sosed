# Sosed — mini social network backend

REST API for a small social network: users, posts, comments, likes, JWT auth,
email verification, and background cleanup of stale accounts.

## Stack

- **FastAPI** (async) + **Pydantic v2**
- **PostgreSQL** with **SQLAlchemy 2.0** (async, `asyncpg`) and **Alembic** migrations
- **Celery** + **Redis** for background / periodic tasks
- **Mailpit** as a local SMTP catcher for email verification
- **Docker Compose** for the full stack

## Quick start

```bash
cp .env.example .env 
docker compose up
```

This starts everything and runs migrations automatically. Once up:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Mailpit (sent emails): <http://localhost:8025>

| Service | Purpose | Host port |
|---|---|---|
| `app` | FastAPI (migrations + uvicorn) | 8000 |
| `db` | PostgreSQL 18 | 5433 |
| `redis` | Celery broker/backend | 6379 |
| `mailpit` | SMTP catcher + web inbox | 1025 / 8025 |
| `worker` | Celery worker | — |
| `beat` | Celery scheduler | — |

Stop with `docker compose down` (add `-v` to also drop the database volume).

## Email verification (local)

There is **no real SMTP** in the default setup — verification emails are captured
by **Mailpit** instead of being delivered. To verify an account:

1. `POST /auth/register` — a verification email is queued and sent to Mailpit.
2. Open the Mailpit inbox at <http://localhost:8025> and open the message.
3. Copy the link (`.../auth/verify-email?token=...`) and open it, or call
   `GET /auth/verify-email?token=<token>` directly.

The token expires after `EMAIL_VERIFICATION_EXPIRE_HOURS` (default 24h).
Use `POST /auth/request-verification` (authenticated) to resend.

**Real email:** point the SMTP settings at a real provider in `.env`
(`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_TLS=true`) and
remove the `SMTP_HOST`/`SMTP_PORT` overrides on the `app`/`worker`/`beat`
services in `docker-compose.yml`. No code changes are needed.

## API

Full interactive spec at `/docs`. Main endpoints:

| Method | Path | Notes |
|---|---|---|
| POST | `/auth/register` | Create account (`is_verified=false`) |
| POST | `/auth/login` | Returns JWT access token (rate-limited) |
| GET | `/auth/me` | Current user |
| GET | `/auth/verify-email?token=` | Verify email |
| POST | `/auth/request-verification` | Resend verification email |
| PATCH | `/users/me` | Update own profile |
| GET | `/posts` | List — `page`, `size`, `search`, `date_from`, `date_to` |
| POST | `/posts` | Create (verified only) |
| GET | `/posts/{id}` | Detail with comments |
| PATCH / DELETE | `/posts/{id}` | Author only |
| GET / POST | `/posts/{id}/comments` | List / add (add: verified only) |
| DELETE | `/posts/{post_id}/comments/{comment_id}` | Author only |
| POST / DELETE | `/posts/{id}/like` | Like / unlike |
| GET | `/feed` | Users with their posts and likes (paginated) |
| POST | `/internal/cleanup-unverified` | Manually trigger cleanup task |

### Example

```bash
# register
curl -X POST localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"a@example.com","username":"alice","full_name":"Alice A","password":"password123"}'

# ...verify via Mailpit (see above), then:
TOKEN=$(curl -s -X POST localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"a@example.com","password":"password123"}' | jq -r .access_token)

# create a post
curl -X POST localhost:8000/posts -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"title":"hello world","content":"first post"}'

# feed
curl localhost:8000/feed
```

## Authorization

- **Unverified** users can log in, browse posts, and like posts.
- **Verified** users can additionally create posts and comments.
- Users can edit/delete **only their own** posts and comments.
- A user **cannot** like their own post, and can like a post only once.

Violations return the appropriate status (`401` unauthenticated, `403` forbidden,
`404` not found, `409` conflict).

## Background tasks

Celery worker + beat, backed by Redis:

- `cleanup_unverified_users` — hourly; deletes unverified users older than
  `UNVERIFIED_USER_RETENTION_HOURS`.
- `delete_old_posts` — daily; deletes posts older than `POST_RETENTION_DAYS`
  (disabled when `0`).
- `send_verification_email` — sends the verification email on registration.

## Configuration

All settings come from environment variables (see `.env.example`). Key ones:

| Variable | Default | Purpose |
|---|---|---|
| `JWT_SECRET_KEY` | — | Token signing secret (set a strong value) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token lifetime |
| `EMAIL_VERIFICATION_EXPIRE_HOURS` | 24 | Verification token lifetime |
| `UNVERIFIED_USER_RETENTION_HOURS` | 48 | Cleanup threshold |
| `POST_RETENTION_DAYS` | 0 | Post TTL (0 = off) |
| `LOGIN_RATE_LIMIT` | 5/minute | Login attempts per IP |
| `SMTP_*`, `APP_BASE_URL` | Mailpit | Email delivery |

## Project structure

```
app/
├── api/            # routers + dependencies (auth, users, posts, comments, likes, feed, internal)
│   ├── deps.py     # DB session, current-user, verified-user, filters
│   └── routes/
├── core/           # config, security (hashing/JWT), exceptions, rate limiter
├── db/             # async engine/session + sync session (for workers)
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic request/response models
├── services/       # business logic (HTTP-agnostic)
└── workers/        # Celery app + tasks
migrations/         # Alembic
```

Layering: **routes** (HTTP) → **services** (business rules) → **models** (DB).
Services raise domain errors that a single handler maps to HTTP status codes.

## Migrations

Migrations run automatically on `app` startup. To run manually:

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "message"
```

## Local development (without Docker)

```bash
uv sync
docker compose up db redis mailpit      # infra only
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
uv run celery -A app.workers.celery_app:celery_app worker --loglevel=info
uv run celery -A app.workers.celery_app:celery_app beat --loglevel=info
```
