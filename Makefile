# ---------------------------------------------------------------------------
# fastapi-boilerplate — task runner
#
# Run `make` (or `make help`) for the list of targets. Each section below
# groups related commands.
# ---------------------------------------------------------------------------

SHELL := /bin/bash
.DEFAULT_GOAL := help

POETRY        ?= poetry
PY            ?= $(POETRY) run python
PYTEST        ?= $(POETRY) run pytest

ENV_FILE      ?= .env
LOCAL_FILE    := compose/local/local.yml
PROD_FILE     := compose/production/prod.yml
COMPOSE_LOCAL := docker compose --env-file $(ENV_FILE) -f $(LOCAL_FILE)
COMPOSE_PROD  := docker compose --env-file $(ENV_FILE) -f $(PROD_FILE)

# Service to target with shell/logs by default (override: `make logs s=worker`).
s ?= web

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

.PHONY: help
help:  ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "; printf "\nUsage: make \033[36m<target>\033[0m\n"} \
		/^## ===/ { s = $$0; gsub(/^## === /, "", s); gsub(/ ===$$/, "", s); printf "\n\033[1m%s\033[0m\n", s } \
		/^[a-zA-Z0-9_-]+:.*?## / { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ---------------------------------------------------------------------------
## === Setup ===
# ---------------------------------------------------------------------------

.PHONY: install install-dev hooks env
install:  ## Install runtime dependencies via Poetry
	$(POETRY) install --without dev

install-dev:  ## Install all dependencies (including dev/test)
	$(POETRY) install

hooks:  ## Install pre-commit hooks
	$(POETRY) run pre-commit install

env:  ## Copy .env.example to .env if .env is missing
	@test -f $(ENV_FILE) && echo "$(ENV_FILE) already exists, skipping." \
		|| (cp .env.example $(ENV_FILE) && echo "Created $(ENV_FILE) from .env.example")

# ---------------------------------------------------------------------------
## === Code quality ===
# ---------------------------------------------------------------------------

.PHONY: lint format check
lint:  ## Lint with ruff
	$(POETRY) run ruff check .

format:  ## Format with ruff
	$(POETRY) run ruff format .

check:  ## Run the full pre-commit suite over all files
	$(POETRY) run pre-commit run --all-files

# ---------------------------------------------------------------------------
## === Tests ===
# ---------------------------------------------------------------------------

.PHONY: test test-collect test-db
test:  ## Run the test suite
	$(PYTEST)

test-collect:  ## Collect tests without running (sanity check)
	$(PYTEST) --collect-only -q

test-db:  ## Create the Postgres test DB (POSTGRES_DB_TEST or POSTGRES_DB+"_test")
	@set -a; . ./$(ENV_FILE); set +a; \
		DB_NAME=$${POSTGRES_DB_TEST:-$${POSTGRES_DB}_test}; \
		echo "Creating database $$DB_NAME on $$POSTGRES_SERVER:$$POSTGRES_PORT"; \
		PGPASSWORD=$$POSTGRES_PASSWORD createdb -h $$POSTGRES_SERVER -p $$POSTGRES_PORT -U $$POSTGRES_USER $$DB_NAME

# ---------------------------------------------------------------------------
## === Dev (host) ===
# ---------------------------------------------------------------------------

.PHONY: runserver worker superuser shell
runserver:  ## Run the FastAPI dev server (uvicorn, host)
	$(PY) manage.py runserver --reload

worker:  ## Run the dramatiq worker (host)
	$(PY) manage.py runworker

superuser:  ## Create a superuser interactively
	$(PY) manage.py create_superuser

shell:  ## Open a Poetry shell
	$(POETRY) shell

# ---------------------------------------------------------------------------
## === Migrations ===
# ---------------------------------------------------------------------------

.PHONY: migrate makemigrations
migrate:  ## Apply pending Alembic migrations
	$(PY) manage.py migrate

makemigrations:  ## Generate a new Alembic revision (override message: m="my change")
	$(PY) manage.py makemigrations -m "$(or $(m),auto migration)"

# ---------------------------------------------------------------------------
## === Docker — local ===
# ---------------------------------------------------------------------------

.PHONY: up down build rebuild logs ps restart d-shell d-dbshell d-migrate d-test
up:  ## Start the local stack (web + worker + postgres + redis)
	$(COMPOSE_LOCAL) up -d --build

down:  ## Stop the local stack (preserves volumes)
	$(COMPOSE_LOCAL) down

build:  ## Build local images
	$(COMPOSE_LOCAL) build

rebuild:  ## Rebuild local images with no cache
	$(COMPOSE_LOCAL) build --no-cache

logs:  ## Tail logs (override service: `make logs s=worker`)
	$(COMPOSE_LOCAL) logs -f $(s)

ps:  ## List running services
	$(COMPOSE_LOCAL) ps

restart:  ## Restart a service (override: `make restart s=worker`)
	$(COMPOSE_LOCAL) restart $(s)

d-shell:  ## Bash into the web container
	$(COMPOSE_LOCAL) exec web bash

d-dbshell:  ## psql into the postgres container
	$(COMPOSE_LOCAL) exec postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-db_name}

d-migrate:  ## Apply migrations inside the web container
	$(COMPOSE_LOCAL) exec web python manage.py migrate

d-test:  ## Run the test suite inside the web container
	$(COMPOSE_LOCAL) exec web pytest

# ---------------------------------------------------------------------------
## === Docker — production ===
# ---------------------------------------------------------------------------

.PHONY: prod-up prod-down prod-build prod-logs prod-ps prod-migrate prod-shell
prod-up:  ## Start the production stack (web + worker + postgres + redis + traefik)
	$(COMPOSE_PROD) up -d --build

prod-down:  ## Stop the production stack (preserves volumes)
	$(COMPOSE_PROD) down

prod-build:  ## Build production images
	$(COMPOSE_PROD) build

prod-logs:  ## Tail production logs (override service: `make prod-logs s=traefik`)
	$(COMPOSE_PROD) logs -f $(s)

prod-ps:  ## List running production services
	$(COMPOSE_PROD) ps

prod-migrate:  ## Apply migrations against the production stack
	$(COMPOSE_PROD) exec web python manage.py migrate

prod-shell:  ## Bash into the production web container
	$(COMPOSE_PROD) exec web bash

# ---------------------------------------------------------------------------
## === Cleanup ===
# ---------------------------------------------------------------------------

.PHONY: clean nuke
clean:  ## Remove __pycache__, .pytest_cache, build artifacts
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
	rm -rf dist build *.egg-info

nuke:  ## Stop local stack AND delete its volumes (DESTRUCTIVE)
	$(COMPOSE_LOCAL) down -v
