import os
import select
import sys
import traceback

from cmd_manager import BaseCommand


class Command(BaseCommand):
    help = (
        "Runs a Python interactive interpreter. Tries to use IPython or "
        "bpython, if one of them is available. Any standard input is executed "
        "as code."
    )

    requires_system_checks = []
    shells = ["python"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = self.kwargs.get("db")

    # def ipython(self, options):
    #     from IPython import start_ipython
    #
    #     start_ipython(argv=[])
    #
    # def bpython(self, options):
    #     import bpython
    #
    #     bpython.embed()

    def python(self, options):
        import code

        # Set up a dictionary to serve as the environment for the shell.
        imported_objects = {}

        # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
        # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
        if not options.get("no_startup"):
            for pythonrc in [os.environ.get("PYTHONSTARTUP"), os.path.expanduser("~/.pythonrc.py")]:
                if not pythonrc:
                    continue
                if not os.path.isfile(pythonrc):
                    continue
                with open(pythonrc) as handle:
                    pythonrc_code = handle.read()
                # Match the behavior of the cpython shell where an error in
                # PYTHONSTARTUP prints an exception and continues.
                try:
                    exec(compile(pythonrc_code, pythonrc, "exec"), imported_objects)
                except Exception:
                    traceback.print_exc()

        # By default, this will set up readline to do tab completion and to read and
        # write history to the .python_history file, but this can be overridden by
        # $PYTHONSTARTUP or ~/.pythonrc.py.
        try:
            hook = sys.__interactivehook__
        except AttributeError:
            # Match the behavior of the cpython shell where a missing
            # sys.__interactivehook__ is ignored.
            pass
        else:
            try:
                hook()
            except Exception:
                # Match the behavior of the cpython shell where an error in
                # sys.__interactivehook__ prints a warning and the exception
                # and continues.
                print("Failed calling sys.__interactivehook__")
                traceback.print_exc()

        # Set up tab completion for objects imported by $PYTHONSTARTUP or
        # ~/.pythonrc.py.
        try:
            import readline
            import rlcompleter

            readline.set_completer(rlcompleter.Completer(imported_objects).complete)
        except ImportError:
            pass

        # Start the interactive interpreter.
        code.interact(local=imported_objects)

    def run(self, *args, **kwargs):
        # Execute stdin if it has anything to read and exit.
        # Not supported on Windows due to select.select() limitations.
        if sys.platform != "win32" and not sys.stdin.isatty() and select.select([sys.stdin], [], [], 0)[0]:
            exec(sys.stdin.read(), globals())
            return

        available_shells = [kwargs.get("interface")] if kwargs.get("interface") else self.shells

        for shell in available_shells:
            try:
                return getattr(self, shell)(kwargs)
            except ImportError:
                pass
