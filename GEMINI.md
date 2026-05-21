# Gemini Project Context: Fast FastAPI Boilerplate (Minimalist Version)

This project is a streamlined FastAPI boilerplate, stripped down to its core essentials for a fresh start.

## Project Overview

- **Framework:** [FastAPI](https://fastapi.tiangolo.com)
- **Architecture:** Clean Core.
    - `src/core/`: Essential framework logic (App Factory, Database, Settings).
    - `src/utils/`: Common project utilities.
- **Database:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async) with [Alembic](https://alembic.sqlalchemy.org/) for migrations.
- **Data Validation:** [Pydantic V2](https://docs.pydantic.dev/latest/).
- **CLI Management:** Custom `manage.py` for project tasks.

## Project Structure

```text
.
├── src/                        # Source code
│   ├── core/                   # Core framework logic
│   │   ├── setup.py            # ApplicationFactory implementation
│   │   ├── db/                 # Database connectivity and base models
│   │   └── settings/           # Environment-based settings
│   ├── migrations/             # Alembic migration scripts
│   ├── scripts/                # CLI task scripts
│   └── utils/                  # Shared utilities
├── manage.py                   # Central CLI
└── pyproject.toml              # Dependencies
```

## Building and Running

### Prerequisites
- Python 3.11+
- [Poetry](https://python-poetry.org/)
- PostgreSQL (recommended to run via Docker)

### Installation
```bash
poetry install
```

### Running the Development Server
**Note: Application entry point (application.py) is currently removed. You must define your FastAPI app instance before running the server.**

```bash
python manage.py runserver
```

### Database Migrations
```bash
# Generate a new migration
python manage.py makemigrations -m "Description of changes"

# Apply migrations
python manage.py migrate
```

## Development Conventions

### Core Logic
The application is intended to be initialized via the `ApplicationFactory` in `src/core/setup.py`.

### Key Files
- `src/core/setup.py`: Contains the logic to bootstrap the FastAPI instance.
- `manage.py`: The primary interface for developer CLI commands.
