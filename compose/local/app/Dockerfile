# syntax=docker/dockerfile:1.6
# Build context is the repo root (set via compose `build.context: ../../`).

# ---------- requirements stage ----------
FROM python:3.11-slim AS requirements

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /tmp
COPY pyproject.toml poetry.lock* /tmp/

# Include dev deps so tests / pre-commit can run inside the container.
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev


# ---------- runtime stage ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/code

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY --from=requirements /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /code

EXPOSE 8000

CMD ["uvicorn", "src.core.setup:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
