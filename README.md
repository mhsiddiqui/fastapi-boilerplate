# FastAPI Boilerplate

An opinionated, production-ready FastAPI starter built around SQLAlchemy 2.0,
Pydantic V2, Alembic, Dramatiq, and Traefik. Versioned REST API, JWT auth,
admin dashboard, generic pagination, rate-limited auth endpoints, structured
logging, and a complete Docker setup for both local development and production
deployment behind HTTPS.

---

## Table of contents

1. [Features](#features)
2. [Tech stack](#tech-stack)
3. [Quick start](#quick-start)
4. [Project structure](#project-structure)
5. [Configuration](#configuration)
6. [Make targets](#make-targets)
7. [Application architecture](#application-architecture)
8. [API reference](#api-reference)
9. [Pagination](#pagination)
10. [Background tasks (Dramatiq)](#background-tasks-dramatiq)
11. [Database & migrations](#database--migrations)
12. [Admin dashboard](#admin-dashboard)
13. [Testing](#testing)
14. [Docker — local](#docker--local)
15. [Docker — production with Traefik](#docker--production-with-traefik)
16. [Conventions](#conventions)
17. [License](#license)

---

## Features

- **FastAPI** with versioned routers (`/api/v1/...`) and OpenAPI docs gated off in production
- **JWT authentication** — access + refresh tokens with a `type` claim so a leaked access token cannot be used at the refresh endpoint
- **SQLAlchemy 2.0 async** with `MappedAsDataclass(kw_only=True)` models, both async (runtime) and sync (management commands) engines
- **Alembic** migrations wired to the application's metadata; handwritten initial revision included
- **Pydantic V2** with `pydantic-settings`, environment-selected settings via class composition
- **Generic Django-style pagination** (`Page[T]` with `items`, `total`, `pages`, `current`, `next`, `previous` PageLinks carrying URLs)
- **Rate limiting** on auth endpoints via `slowapi`
- **CORS** configurable from env (origins, credentials, methods, headers)
- **Structured logging** via `logging.dictConfig` — uvicorn workers inherit it
- **Health probe** at `GET /health` that verifies the DB with `SELECT 1`
- **Dramatiq** + Redis broker for background jobs, with a `runworker` CLI subcommand
- **Soft-delete mixin** (`is_deleted`, `deleted_at`, `soft_delete()`) alongside timestamp/UUID mixins
- **starlette-admin** dashboard with session-based auth
- **Click-based `manage.py`** for `runserver`, `migrate`, `makemigrations`, `runworker`, `create_superuser`, auto-discovering scripts under `src/scripts/`
- **Docker** stacks for both local development (uvicorn `--reload`, bind-mounted code, Postgres, Redis, worker) and production (gunicorn + uvicorn workers, non-root user, Postgres, Redis, worker, Traefik with Let's Encrypt)
- **Async pytest suite** with Postgres test DB, fixture-isolated rows, and disabled rate limiter
- **Makefile** with ~30 short-form targets and a colorized `make help`

---

## Tech stack

| Layer | Choice |
|---|---|
| Framework | FastAPI 0.115 |
| Validation | Pydantic V2 (with `pydantic-settings`) |
| ORM | SQLAlchemy 2.0 (async + sync engines) |
| Migrations | Alembic |
| DB | PostgreSQL 16 |
| Cache / broker | Redis 7 |
| Background tasks | Dramatiq (Redis broker) |
| Auth | python-jose (JWT) + bcrypt |
| Admin | starlette-admin (session auth) |
| Rate limit | slowapi |
| Tests | pytest, pytest-asyncio, httpx, asgi-lifespan |
| Lint / format | ruff |
| Pre-commit | pre-commit, yesqa, mdformat |
| Server | uvicorn (dev) / gunicorn + uvicorn workers (prod) |
| Reverse proxy | Traefik v2 (Docker provider, Let's Encrypt) |
| Packaging | Poetry |
| Python | 3.11 |

---

## Quick start

### Prerequisites

- Python 3.11
- Poetry 1.8+
- Docker + Docker Compose v2 (optional, for the Docker workflow)
- A running PostgreSQL 16 if you run the host workflow without Docker

### Option A — Docker (recommended)

```bash
git clone <this-repo>
cd fastapi-boilerplate
make env                  # copy .env.example → .env
make up                   # build & start: web + worker + postgres + redis
make d-migrate            # run Alembic migrations inside the container
open http://localhost:8000/docs
```

### Option B — Host (Poetry)

```bash
git clone <this-repo>
cd fastapi-boilerplate

make env                  # copy .env.example → .env
make install-dev          # poetry install (incl. dev deps)
make hooks                # install pre-commit hooks

# Bring up Postgres + Redis yourself (or use docker compose just for those).
make migrate              # alembic upgrade head
make runserver            # uvicorn on http://127.0.0.1:8000
```

For tests, also create the test DB:

```bash
make test-db              # creates ${POSTGRES_DB}_test
make test
```

---

## Project structure

```
fastapi-boilerplate/
├── manage.py                       # Click CLI (runserver / migrate / runworker / ...)
├── alembic.ini                     # script_location = src/migrations
├── Makefile                        # ~30 short-form targets; `make help` for the list
├── pyproject.toml
├── .env.example                    # documented config keys
├── compose/
│   ├── local/
│   │   ├── app/Dockerfile          # dev image (uvicorn --reload, dev deps)
│   │   └── local.yml               # web + worker + postgres + redis
│   └── production/
│       ├── app/Dockerfile          # slim image, non-root, gunicorn
│       ├── prod.yml                # production stack + traefik
│       └── traefik/                # Traefik image + static config
│           ├── Dockerfile
│           └── traefik.yml
├── src/
│   ├── core/
│   │   ├── setup.py                # ApplicationFactory + `app` instance
│   │   ├── logging.py              # dictConfig wrapper
│   │   ├── pagination.py           # Page[T] + PaginationParams + paginate()
│   │   ├── rate_limit.py           # slowapi Limiter
│   │   ├── security.py             # password hash / JWT encode-decode
│   │   ├── exceptions/             # CustomValidationException + handlers
│   │   ├── settings/               # base.py + local.py / production.py mixins
│   │   └── db/
│   │       ├── base.py             # Base = MappedAsDataclass(kw_only=True)
│   │       ├── database.py         # async + sync engines, get_async_db
│   │       └── mixins.py           # TimeStampedModel, SoftDeleteMixin, UUIDMixin
│   ├── app/                        # HTTP layer
│   │   ├── __init__.py             # api_router (/api) + root_router
│   │   ├── health.py               # GET /health
│   │   └── v1/
│   │       ├── auth/api.py         # POST /login, POST /refresh
│   │       └── user/api.py         # POST /users, GET /users, GET /me, PATCH /users/{id}
│   ├── admin/                      # starlette-admin (auth.py, views.py)
│   ├── tasks/                      # Dramatiq actors (RedisBroker registered here)
│   ├── models/                     # SQLAlchemy models (imported by Alembic)
│   ├── migrations/                 # Alembic env + revisions
│   └── scripts/                    # Click subcommands auto-discovered by manage.py
└── tests/
    ├── conftest.py                 # async fixtures, Postgres test DB
    ├── helpers.py                  # register_user, login, auth_header
    ├── test_health.py
    ├── test_auth.py
    └── test_user.py
```

---

## Configuration

All settings come from `.env` (loaded via `starlette.config.Config`). The
example file (`.env.example`) documents every key. The most important:

```ini
# environment switch — selects src/core/settings/{local,production}.py
ENVIRONMENT=local

# app
APP_NAME="My API"
APP_DESCRIPTION="…"
APP_VERSION=0.1
LOG_LEVEL=INFO

# CORS (defaults shown — comma-separated lists)
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# postgres (host workflow uses 127.0.0.1; Docker compose overrides to `postgres`)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_SERVER=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=db_name

# crypto / JWT
SECRET_KEY=<generate with: python -c 'import secrets; print(secrets.token_hex(32))'>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# redis (host workflow uses localhost; Docker compose overrides to `redis`)
REDIS_CACHE_HOST=localhost
REDIS_CACHE_PORT=6379
REDIS_QUEUE_HOST=localhost
REDIS_QUEUE_PORT=6379

# production traefik
DOMAIN_NAME=api.example.com
LETSENCRYPT_EMAIL=admin@example.com
TRAEFIK_DASHBOARD_HOST=traefik.example.com
TRAEFIK_DASHBOARD_AUTH=                 # optional htpasswd; `$` escaped as `$$`
```

### How settings work

`src/core/settings/__init__.py` reads `ENVIRONMENT`, imports
`src.core.settings.{ENVIRONMENT}`, and instantiates that module's `Settings`
class. Per-environment files multiply inherit from setting *mixins* in
`base.py` (`AppSettings`, `CryptSettings`, `DatabaseSettings`,
`RedisCacheSettings`, `RedisQueueSettings`, `MediaSettings`,
`EnvironmentSettings`).

To add a new config group: add a `BaseSettings` subclass in `base.py`, then
mix it into the per-environment `Settings`.

Middlewares are declared as data on the settings object —
`AppSettings.MIDDLEWARES: list[Middleware]`, where
`Middleware(class_path, args, kwargs)` resolves the class lazily via
`pydoc.locate`. `ApplicationFactory.add_middlewares` iterates this list. So
middlewares are configured per environment, not in code at the app boundary.

---

## Make targets

`make` (or `make help`) lists everything. The most-used:

| Goal | Command |
|---|---|
| First-time host setup | `make install-dev && make hooks && make env` |
| Run dev server (host) | `make runserver` |
| Run worker (host) | `make worker` |
| Run tests | `make test` |
| Lint | `make lint` |
| Format | `make format` |
| Pre-commit on all files | `make check` |
| Apply migrations | `make migrate` |
| New migration | `make makemigrations m="add foo table"` |
| Create test DB | `make test-db` |
| Bring up local Docker stack | `make up` |
| Tail logs | `make logs` (or `make logs s=worker`) |
| Bash into web container | `make d-shell` |
| psql into the postgres container | `make d-dbshell` |
| Migrate inside Docker | `make d-migrate` |
| Run tests inside Docker | `make d-test` |
| Bring down local stack | `make down` |
| Wipe local DB/Redis volumes | `make nuke` |
| Bring up production stack | `make prod-up` |
| Tail traefik logs | `make prod-logs s=traefik` |

Service overrides use `make <target> s=<service>` (default `web`), so the same
`logs` / `restart` targets work for `worker`, `postgres`, `redis`, `traefik`.

---

## Application architecture

### Bootstrap: `ApplicationFactory`

`src/core/setup.py` defines an `ApplicationFactory` that:

1. Pulls metadata (title, description, contact, license) from `AppSettings`
2. Builds a lifespan that optionally runs `Base.metadata.create_all` on startup
3. Hides `/docs`, `/redoc`, `/openapi.json` when `ENVIRONMENT=production`
4. Wires exception handlers (Pydantic validation errors and a custom
   `CustomValidationException` both normalize to `{"detail": [{"field": ..., "message": ...}]}`)
5. Adds CORS from `AppSettings.CORS_*` and any extra middlewares from
   `settings.MIDDLEWARES`
6. Installs slowapi's rate-limit middleware and exception handler

The instance lives at `src.core.setup:app` and includes the `api_router`
(`/api/v1/...`), `root_router` (`/health`), and mounts the admin app.

### Routing layout

- `src/app/__init__.py` — `api_router` (`/api`) + `root_router`
- `src/app/v1/__init__.py` — combines feature routers under `/v1`
- `src/app/v1/<feature>/api.py` — endpoints
- `src/app/v1/<feature>/schemas.py` — Pydantic request/response models

Adding a feature `widgets`:

```python
# src/app/v1/widgets/api.py
from fastapi import APIRouter
router = APIRouter(prefix="/widgets", tags=["widgets"])

# src/app/v1/widgets/__init__.py
from .api import router

# src/app/v1/__init__.py
from src.app.v1.widgets import router as widgets_router
v1_router.include_router(widgets_router)
```

### Database layer

- `src/core/db/database.py` builds **both** an async engine (`async_engine`,
  used at runtime via the `get_async_db` dependency) and a sync engine
  (`get_sync_db()`, used by management commands)
- Postgres URL is composed from `DatabaseSettings` (or use `POSTGRES_URL` to
  pass a full DSN)
- `Base` is `DeclarativeBase` + `MappedAsDataclass(kw_only=True)`, so all
  fields are keyword-only — this eliminates the "default before non-default"
  ordering trap when mixing mixins with defaulted columns
- Reusable mixins in `src/core/db/mixins.py`: `UUIDMixin` (UUID PK with
  `gen_random_uuid()` server default), `TimeStampedModel`
  (`created`, `modified` with `func.now()`), `SoftDeleteMixin`
  (`is_deleted`, `deleted_at`, `soft_delete()`)

---

## API reference

All API endpoints live under `/api/v1`. The `/health` probe is unversioned.

### Health

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | — | Liveness + readiness (issues `SELECT 1`; returns 503 if DB unreachable) |

### Auth (`/api/v1/auth`)

| Method | Path | Auth | Rate limit | Description |
|---|---|---|---|---|
| POST | `/login` | — | 5/min | Exchange `{email, password}` → `{access_token, refresh_token, token_type}` |
| POST | `/refresh` | — | 10/min | Exchange `{refresh_token}` → `{access_token, token_type}` |

Tokens carry a `type` claim (`access` or `refresh`). The refresh endpoint
rejects access tokens — leaking an access token does not extend a session.

### Users (`/api/v1/users`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `` | — | Register a new user. 409 if the email or username is taken; 422 if the password is too short. |
| GET | `/me` | Bearer | Current user |
| GET | `` | Bearer | Paginated list (`Page[UserRead]`, see below) |
| PATCH | `/{user_id}` | Bearer | Update own user. 403 if `{user_id}` belongs to someone else. The `UserUpdate` schema is `extra="forbid"`, so `is_superuser` / `password` are rejected with 422. |

---

## Pagination

`src/core/pagination.py` exposes a generic Django-style page-number
pagination wrapper:

```python
@router.get("", response_model=Page[UserRead])
async def list_users(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(get_current_user),
    params: PaginationParams = Depends(),
) -> Page[UserRead]:
    stmt = select(User).order_by(User.created.desc())
    return await paginate(request, db, stmt, UserRead, params)
```

Query parameters: `page` (1-indexed, default 1), `page_size` (default 50,
capped at 200). Response shape:

```json
{
  "items": [...],
  "total": 3,
  "limit": 2,
  "offset": 0,
  "pages": 2,
  "current": {"page": 1, "url": "http://.../users?page=1&page_size=2"},
  "next":    {"page": 2, "url": "http://.../users?page=2&page_size=2"},
  "previous": null
}
```

`paginate()` works with any `select(...)` statement and any Pydantic
response schema — drop it into a new endpoint and you get pagination for
free.

---

## Background tasks (Dramatiq)

`src/tasks/__init__.py` configures the Dramatiq Redis broker and imports all
actor modules so they register with the broker on import:

```python
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from src.core.settings import settings

dramatiq.set_broker(RedisBroker(
    host=settings.REDIS_QUEUE_HOST,
    port=settings.REDIS_QUEUE_PORT,
))

from src.tasks.emails import send_welcome_email  # noqa: E402, F401
```

Adding an actor:

```python
# src/tasks/emails.py
import dramatiq

@dramatiq.actor(max_retries=3, min_backoff=1_000, max_backoff=60_000)
def send_welcome_email(user_id: str, email: str) -> None:
    ...
```

Then import it in `src/tasks/__init__.py` (or any module that's imported on
worker boot) so it registers.

Running the worker:

```bash
make worker                                  # host
# or, inside Docker, the `worker` service is started by `make up`
```

---

## Database & migrations

Alembic is configured to read `sqlalchemy.url` from `DatabaseSettings` and to
target `Base.metadata`. Models must be imported somewhere reachable from
`src/core/db/database.py` (e.g. via `src/models/__init__.py`) before
autogenerate will see them.

```bash
make makemigrations m="add widgets"          # alembic revision --autogenerate
make migrate                                 # alembic upgrade head
# inside Docker:
make d-migrate
```

The initial revision `src/migrations/versions/20260519_0001_create_users.py`
creates the `users` table.

### Models

Models use SQLAlchemy 2.0 + `MappedAsDataclass` semantics
(`mapped_column(..., default=...)`), not classic ORM syntax. Example:

```python
# src/models/user.py
from sqlalchemy.orm import Mapped, mapped_column
from src.core.db.base import Base
from src.core.db.mixins import UUIDMixin, TimeStampedModel, SoftDeleteMixin

class User(UUIDMixin, TimeStampedModel, SoftDeleteMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    password: Mapped[str]            # bcrypt hash
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
```

---

## Admin dashboard

starlette-admin is mounted at `/admin`:

- `src/admin/auth.py` — `AuthProvider` against the `User` table (superusers only)
- `src/admin/views.py` — `UserView` with sensitive fields (`password`,
  `is_superuser`) hidden from non-superuser editors
- `src/admin/__init__.py` — admin instance + `mount_to(app)` call in
  `src/core/setup.py`

`SessionMiddleware` is registered automatically; the cookie is signed by
`SECRET_KEY`.

Create the first superuser:

```bash
make superuser                                # interactive
```

---

## Testing

Tests run against a dedicated Postgres database. Override the name via
`POSTGRES_DB_TEST`; otherwise `${POSTGRES_DB}_test` is used. Create it once:

```bash
make test-db
```

Then:

```bash
make test                                     # all tests
make test-collect                             # collect-only (no execution)
poetry run pytest tests/test_user.py::test_register_creates_user
```

Test infrastructure (in `tests/conftest.py`):

- Session-scoped `_setup_database` fixture drops/creates schema once via
  `Base.metadata.create_all`
- Function-scoped `_truncate_tables` autouse fixture wipes rows between
  tests so order doesn't matter
- `client` fixture overrides `get_async_db` to use the same `AsyncSession` as
  the test
- `limiter.enabled = False` at module import — rate limits don't fight
  the suite

Helpers in `tests/helpers.py`: `register_user`, `login`, `auth_header`.

Coverage at a glance:

- `tests/test_health.py` — happy path + DB-down 503 via per-test
  `dependency_overrides` swap
- `tests/test_auth.py` — token pair, wrong password 401, unknown email 401,
  refresh issues new access, refresh-rejects-access-token
- `tests/test_user.py` — register success/duplicate/422, `/me` auth gate,
  list auth gate, pagination shape + last-page, own-update, forbidden
  cross-update, `extra="forbid"` rejection

---

## Docker — local

```bash
docker compose --env-file .env -f compose/local/local.yml up --build
# or:
make up
```

The `--env-file .env` flag is required so `${VAR}` interpolation reads the
repo-root `.env` (Compose otherwise looks for a `.env` next to the compose
file).

Services:

| Service | Image | Purpose |
|---|---|---|
| `web` | built from `compose/local/app/Dockerfile` | uvicorn `--reload`, repo bind-mounted at `/code` |
| `worker` | same image | `dramatiq src.tasks` |
| `postgres` | `postgres:16` | port 5432 exposed |
| `redis` | `redis:7-alpine` | port 6379 exposed |

Inside compose, `POSTGRES_SERVER` / `REDIS_*_HOST` are overridden to the
service names (`postgres`, `redis`); the host-side `.env` keeps `127.0.0.1`
for running outside Docker.

---

## Docker — production with Traefik

```bash
docker compose --env-file .env -f compose/production/prod.yml up -d --build
# or:
make prod-up
```

Services:

| Service | Image | Notes |
|---|---|---|
| `web` | `compose/production/app/Dockerfile` | gunicorn + uvicorn workers, non-root `app` user. No host port — only reachable through Traefik. |
| `worker` | same image | `dramatiq --processes 2 --threads 8 src.tasks` |
| `postgres` | `postgres:16` | No host port. Named volume `postgres_data`. |
| `redis` | `redis:7-alpine` | No host port. Named volume `redis_data`. |
| `traefik` | `compose/production/traefik/Dockerfile` | Listens on `:80` and `:443`. HTTP→HTTPS redirect at the entrypoint level. Let's Encrypt via HTTP-01 challenge. |

Networks:

- `edge` — Traefik ↔ web. Only services with `traefik.enable=true` and on
  this network are routable from outside.
- `internal` — web ↔ postgres / redis / worker. Postgres and Redis have no
  host ports and are only reachable inside the compose network.

### Traefik routing model

Traefik runs in **Docker-provider mode**. Routes/middlewares live as labels
on the `web` service in `prod.yml`:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.docker.network=edge"
  - "traefik.http.routers.web.rule=Host(`${DOMAIN_NAME}`)"
  - "traefik.http.routers.web.entrypoints=websecure"
  - "traefik.http.routers.web.tls=true"
  - "traefik.http.routers.web.tls.certresolver=letsencrypt"
  - "traefik.http.services.web.loadbalancer.server.port=8000"
```

The static `compose/production/traefik/traefik.yml` only configures
entrypoints, the ACME resolver (HTTP-01 challenge against `letsencrypt`),
and the Docker provider. **There is no per-route static file to keep in
sync** — adding a new service just means adding labels.

The ACME email is injected via the
`TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_EMAIL` environment variable
(set from `LETSENCRYPT_EMAIL` in the compose file), because Traefik does not
template the static YAML.

### Enabling the Traefik dashboard

The dashboard is **off by default**. To enable it:

1. Set `TRAEFIK_DASHBOARD_HOST` (e.g. `traefik.example.com`) with DNS
   pointing at this host
2. Set `TRAEFIK_DASHBOARD_AUTH` to an htpasswd string; escape `$` as `$$` in
   `.env`:
   ```
   TRAEFIK_DASHBOARD_AUTH=admin:$$apr1$$abcd1234$$....
   ```
3. Uncomment the dashboard labels in `compose/production/prod.yml`

### First production deploy

```bash
# on the host
cp .env.example .env
# edit .env: set DOMAIN_NAME, LETSENCRYPT_EMAIL, ENVIRONMENT=production,
# a strong SECRET_KEY, real POSTGRES_* values, etc.

make prod-up
make prod-migrate
```

Traefik will request a Let's Encrypt cert on first inbound HTTPS traffic.
The ACME state is persisted in the `traefik_acme` named volume — back it up.

---

## Conventions

- Line length 120, Python 3.11 target, ruff for lint + format
- Selected lints: `F, E, W, C, UP, I` — `UP006` / `UP007` ignored so both
  `Optional[X]` and `X | None` pass
- `mypy.ini` only enforces `disallow_untyped_defs` under `src.app.*`
- `check-added-large-files --maxkb=750 --enforce-all` — be deliberate
  about committing fixtures or binaries
- The `Settings` class is meant to be extended **by composition**, not by
  editing `base.py` to add app-specific fields. Add a mixin, then mix it in
  per environment.
- Exception handlers normalize Pydantic `loc` tuples to a single `field`
  key — see `src/core/exceptions/handlers.py`. New domain exceptions should
  register their handler there.

---

## License

MIT — see [LICENSE.md](LICENSE.md).
