from typing import Any


class BaseCommand:
    """Base class for defining custom commands."""

    def __init__(self, app: object):
        self.app = app

    def get_arguments(self) -> list[dict]:
        """
        Should be overridden by subclasses to define arguments.
        Each argument should be defined as a dict, e.g.:
        [{'name': 'arg1', 'type': str, 'required': True}, ...]
        """
        return []

    def run(self, *args, **kwargs) -> Any:
        """The logic of the command should be implemented here."""
        raise NotImplementedError("Subclasses must implement the run() method.")
