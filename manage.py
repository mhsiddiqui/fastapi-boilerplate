import click
from alembic import command as alembic_command
from alembic.config import Config
from cmd_manager import ManagementCommandSystem

from src.core.db.database import get_sync_db
from src.core.settings import settings

# Note: Application instance is not yet defined.
management_system = ManagementCommandSystem(app=None, db=get_sync_db())
management_system.register(package="src.scripts")

cli_system = management_system.create_cli()


def get_alembic_config():
    """Get the Alembic configuration from the alembic.ini file."""
    alembic_cfg = Config(str(settings.BASE_DIR / "alembic.ini"))
    return alembic_cfg


@cli_system.command()
@click.option("--host", default="127.0.0.1", help="The host to bind to.")
@click.option("--port", default=8000, help="The port to bind to.")
@click.option("--reload", is_flag=True, default=True, help="Enable auto-reload on code changes.")
@click.option("--workers", default=1, help="Number of worker processes.")
def runserver(host, port, reload, workers):
    """Run the FastAPI development server."""
    import uvicorn

    uvicorn.run(
        "src.core.setup:app",
        host=host,
        port=port,
        reload=reload,
        workers=1 if reload else workers,
    )


@cli_system.command()
@click.option("--message", "-m", default="auto migration", help="Migration message.")
def makemigrations(message):
    """Generate new Alembic migrations."""
    alembic_cfg = get_alembic_config()
    alembic_command.revision(alembic_cfg, message=message, autogenerate=True)
    click.echo(f"Generated new migration with message: {message}")


@cli_system.command()
def migrate():
    """Apply migrations to the database."""
    alembic_cfg = get_alembic_config()
    alembic_command.upgrade(alembic_cfg, "head")
    click.echo("Migrations applied.")


@cli_system.command()
@click.option("--processes", default=1, help="Number of worker processes.")
@click.option("--threads", default=8, help="Threads per process.")
def runworker(processes, threads):
    """Run the dramatiq worker against ``src.tasks``."""
    import os

    os.execvp(
        "dramatiq",
        ["dramatiq", "--processes", str(processes), "--threads", str(threads), "src.tasks"],
    )


if __name__ == "__main__":
    cli_system()
