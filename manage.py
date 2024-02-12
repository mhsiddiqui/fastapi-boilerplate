import click
import uvicorn

from app.backend_pre_start import main as backend_pre_start_main
from app.celeryworker_pre_start import main as celeryworker_pre_start_main
from app.initial_data import main as initial_data_main
from app.tests_pre_start import main as tests_pre_start_main


@click.command()
@click.option(
    "--command",
    type=click.Choice([
        "backend_pre_start", "celeryworker_pre_start", "tests_pre_start", "initial_data", "runserver"
    ], case_sensitive=False),
    default="runserver",
)
def run_command(command):
    if command == 'backend_pre_start':
        return backend_pre_start_main()
    elif command == 'celeryworker_pre_start':
        return celeryworker_pre_start_main()
    elif command == 'tests_pre_start':
        return tests_pre_start_main()
    elif command == 'initial_data':
        return initial_data_main()
    elif command == 'runserver':
        uvicorn.run(
            app="app.main:app",
            reload=True,
            workers=1,
        )


if __name__ == '__main__':
    run_command()
