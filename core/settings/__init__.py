import importlib
import os

SETTINGS_MODULE = os.environ.get("ENVIRONMENT", "local")

setting_module = importlib.import_module(f"core.settings.{SETTINGS_MODULE}")
setting_class = setting_module.Settings

settings = setting_class()
