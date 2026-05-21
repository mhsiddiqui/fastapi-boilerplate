# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo state

This is a **FastAPI boilerplate that is mid-refactor**. The `b5a303e // WIP` commit stripped out the original `core/`, `src/features/*`, `src/tasks/`, auth utilities, email/render utilities, the application entry point, and more. The intent is to rebuild on top of a leaner `src/core/` skeleton.

Concretely, the following are **broken on `main`** and should be expected, not "fixed" in isolation:

- `python manage.py runserver` deliberately errors: "Application entry point (application.py) is missing." There is no `src/core/application.py` defining `app`.
- `tests/conftest.py` imports `from src.core.application import app` → the test suite cannot collect until an `app` is wired up.
- `src/core/settings/local.py` references `OTPSettings`, which is not defined in `src/core/settings/base.py`. Importing settings under `ENVIRONMENT=local` will fail until either `OTPSettings` is added back or removed from the MRO.
- `src/core/settings/production.py` registers a middleware at `src.app.utils.middlewares.client_cache_middleware.ClientCacheMiddleware`, which does not exist.
- `src/scripts/create_superuser.py` imports `src.features.account.models.User` and `src.utils.authentication.get_password_hash` — both deleted. `manage.py` registers `src.scripts` for command discovery, so this file is loaded on any CLI invocation.
- `src/models/` and `src/schemas/` are empty placeholders.

Treat these as the rebuild surface. When asked to "make X work," the first step is usually to verify which of the above is on the path and either reintroduce or stub it explicitly.

## Common commands

Poetry-managed Python 3.11. Always run via Poetry unless inside a container:

```bash
poetry install                                  # install deps
poetry run python manage.py <command>           # run a CLI command
poetry run pytest                               # run tests (currently fails to collect — see above)
poetry run pytest tests/test_user.py::<name>    # single test
poetry run ruff check .                         # lint
poetry run ruff format .                        # format
poetry run pre-commit run --all-files           # full pre-commit suite (ruff, yesqa, mdformat, hygiene hooks)
```

### `manage.py` (Click-based, built on the `cmd-manager` package)

```bash
python manage.py runserver                      # stub — does not start a server yet
python manage.py makemigrations -m "message"    # alembic revision --autogenerate
python manage.py migrate                        # alembic upgrade head
```

Additional commands are auto-discovered from `src/scripts/` (each file defines a `Command(BaseCommand)` class). The discovery line is `management_system.register(package="src.scripts")` in `manage.py:11` — adding a new module under `src/scripts/` makes it appear as a subcommand.

### Docker

Two compose stacks, run from the repo root (each needs `--env-file .env` because Compose looks for `.env` next to the compose file by default):

```bash
# local — web (uvicorn --reload) + worker (dramatiq) + postgres:16 + redis:7
docker compose --env-file .env -f compose/local/local.yml up --build

# production — same services + traefik (Let's Encrypt + HTTP→HTTPS redirect)
docker compose --env-file .env -f compose/production/prod.yml up -d --build
```

Layout:

- `compose/local/local.yml` + `compose/local/app/Dockerfile` — dev image (poetry export `--with dev`, `uvicorn --reload`, repo bind-mounted at `/code`).
- `compose/production/prod.yml` + `compose/production/app/Dockerfile` — slim image (no dev deps, non-root `app` user, gunicorn with uvicorn workers).
- `compose/production/traefik/{Dockerfile,traefik.yml}` — Traefik v2 in Docker-provider mode. Routes are declared as labels on the `web` service in `prod.yml`; the static file only sets entrypoints, the ACME resolver, and the docker provider. No per-route file to maintain.

Inside both stacks, `POSTGRES_SERVER` / `REDIS_*_HOST` are overridden via `environment:` to the service names (`postgres`, `redis`); the host-side `.env` keeps `127.0.0.1` for running outside Docker.

## Architecture

### Settings: environment-selected class composition

`src/core/settings/__init__.py` reads `ENVIRONMENT` (default `"local"`), imports `src.core.settings.{ENVIRONMENT}`, and instantiates that module's `Settings` class. `local.py` and `production.py` each define `Settings` by **multiply inheriting** from setting mixins in `base.py` (`AppSettings`, `CryptSettings`, `DatabaseSettings`, etc.). To add a new config group: add a `BaseSettings` subclass in `base.py`, then mix it into the per-environment `Settings`.

Middlewares are declared as data on the settings object — `AppSettings.MIDDLEWARES: list[Middleware]`, where `Middleware(class_path, args, kwargs)` resolves the class lazily via `pydoc.locate`. `ApplicationFactory.add_middlewares` iterates this list. So middlewares are configured per environment, not in code at the app boundary.

### Application bootstrap: `ApplicationFactory`

`src/core/setup.py` defines `ApplicationFactory`, which:

1. Pulls metadata (title/description/contact/license) from `AppSettings` into FastAPI's constructor kwargs.
2. Builds a lifespan that optionally runs `Base.metadata.create_all` on startup (when settings are a `DatabaseSettings` and `create_tables_on_start=True`).
3. Wires exception handlers via `setup_exception_handlers` (currently handles `RequestValidationError` and a `CustomValidationException`, flattening Pydantic errors to a `{"detail": [...]}` shape with `field` instead of `loc`).
4. Adds middlewares from `settings.MIDDLEWARES`.

The expected re-entry point (not yet present) is something like:

```python
# src/core/application.py
from src.core.setup import ApplicationFactory
app = ApplicationFactory().init()
```

`manage.py runserver`, `tests/conftest.py`, and the Docker `CMD`s all assume this module path.

### Database layer

`src/core/db/database.py` builds **both** an async engine (`async_engine`, used at runtime via the `async_get_db` dependency) and a sync engine (`get_sync_db()`, used only by management commands). The Postgres URL is composed from `DatabaseSettings` fields.

Base model: `Base(DeclarativeBase, MappedAsDataclass)` with two helpers — `Base.query()` returns `select(cls)`, and `serialize()` dumps `__dict__`. Models are expected to use **`MappedAsDataclass` semantics** (`mapped_column(..., default=...)`), not classic SQLAlchemy ORM syntax.

Reusable model mixins live in `src/utils/models.py`: `UUIDMixin` (UUID PK with `gen_random_uuid()` server default), `TimestampMixin` (`created`/`modified`), `SoftDeleteMixin` (`is_deleted` + `deleted_at`).

### Alembic

Config in `alembic.ini` (`script_location = src/migrations`). `src/migrations/env.py` overrides `sqlalchemy.url` from `DatabaseSettings` and uses `async_engine_from_config` for online migrations. `target_metadata = Base.metadata`, so any new model file must be imported somewhere reachable from `src.core.db.database` (e.g., via `src/models/__init__.py`) before autogenerate will see it.

### Exceptions

Custom exceptions live in `src/utils/exceptions/`. `http_exceptions.py` defines `CustomValidationException`; `handlers.py` wires both it and FastAPI's `RequestValidationError` to a single normalizer that rewrites the `loc` tuple into a `field` key. If you add a new domain exception, register its handler in `setup_exception_handlers`.

## Conventions

- Line length 120, Python 3.11 target, Ruff handles lint + format. Ruff selects `F, E, W, C, UP, I` and ignores `UP006/UP007` (so keep `Optional[X]` / `List[X]` if you prefer — both styles pass).
- mypy config (`mypy.ini`) only enforces `disallow_untyped_defs` under `src.app.*`, which doesn't currently exist. The rest of the tree is leniently typed.
- Pre-commit's `check-added-large-files` is set to `--maxkb=750 --enforce-all` — be deliberate about committing fixtures/binaries.
- The `Settings` class is meant to be extended by composition, not by editing `base.py` to add app-specific fields. Add a new mixin.
