import importlib
import os
import pkgutil

import click


class ManagementCommandSystem:
    """System to dynamically register commands and their arguments with Click."""

    def __init__(self, app):
        self.app = app
        self.commands = []

    def register(self, package='scripts'):
        package_module = importlib.import_module(package)
        package_path = os.path.dirname(package_module.__file__)
        for _, module_name, _ in pkgutil.iter_modules([package_path]):
            module = importlib.import_module(f'{package}.{module_name}')
            if hasattr(module, 'Command'):
                self.register_command(name=module_name, command_class=getattr(module, 'Command'))

    def register_command(self, name, command_class):
        """
        Registers a command class and dynamically adds its arguments to Click.
        :param command_class: Subclass of BaseCommand
        """
        command_instance = command_class(app=self.app)
        arguments = command_instance.get_arguments()

        @click.command(name)
        @self._add_arguments(arguments)
        def command(*args, **kwargs):
            # Call the run method of the command instance
            command_instance.run(*args, **kwargs)

        self.commands.append(command)

    def _add_arguments(self, arguments):
        """Dynamically add arguments to a Click command based on the get_arguments method."""

        def decorator(f):
            for arg in reversed(arguments):
                name = arg['name']
                arg_type = arg.get('type', str)
                required = arg.get('required', False)
                f = click.argument(name, type=arg_type, required=required)(f)
            return f

        return decorator

    def create_cli(self):
        """Generate the Click group with dynamically added commands."""

        @click.group()
        def cli():
            pass

        # Add all commands to the Click group
        for command in self.commands:
            cli.add_command(command)

        return cli