import click
import uvicorn
from alembic import command as alembic_command
from alembic.config import Config
from cmd_manager import ManagementCommandSystem

from core.application import app
from core.settings import settings

management_system = ManagementCommandSystem(app=app)
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
    uvicorn.run(app, host=host, port=port, reload=reload, workers=workers)


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


if __name__ == "__main__":
    cli_system()
