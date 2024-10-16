import subprocess

import click
import uvicorn
from alembic.config import Config
from alembic import command as alembic_command
from core.application import app
from core.command.command import ManagementCommandSystem
from core.settings import settings

management_system = ManagementCommandSystem(app=app)
management_system.register(package='src.scripts')

cli = management_system.create_cli()

def get_alembic_config():
    """Get the Alembic configuration from the alembic.ini file."""
    alembic_cfg = Config(str(settings.BASE_DIR / "alembic.ini"))
    return alembic_cfg


@cli.command()
@click.option("--host", default="127.0.0.1", help="The host to bind to.")
@click.option("--port", default=8000, help="The port to bind to.")
@click.option("--reload", is_flag=True, default=True, help="Enable auto-reload on code changes.")
@click.option("--workers", default=1, help="Number of worker processes.")
def runserver(host, port, reload, workers):
    """Run the FastAPI development server."""
    uvicorn.run(app, host=host, port=port, reload=reload, workers=workers)


@cli.command()
@click.option("--message", "-m", default="auto migration", help="Migration message.")
def makemigrations(message):
    """Generate new Alembic migrations."""
    alembic_cfg = get_alembic_config()
    alembic_command.revision(alembic_cfg, message=message, autogenerate=True)
    click.echo(f"Generated new migration with message: {message}")


@cli.command()
def migrate():
    """Apply migrations to the database."""
    alembic_cfg = get_alembic_config()
    alembic_command.upgrade(alembic_cfg, "head")
    click.echo("Migrations applied.")

@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('args', nargs=-1)  # Capture all arguments after the command
def babel(args, **kwargs):
    """This command calls a third-party CLI tool and passes all arguments to it."""
    # Example: Replace `third-party-cli` with the actual CLI command (e.g., 'git')

    print(args)
    print(kwargs)
    command = ['pybabel'] + list(args)

    # Call the third-party CLI using subprocess
    result = subprocess.run(command, capture_output=True, text=True)

    # Output the result (stdout and stderr)
    click.echo(result.stdout)
    click.echo(result.stderr, err=True)


cli.add_command(babel)


if __name__ == '__main__':
    cli()