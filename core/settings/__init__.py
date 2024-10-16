import os
import importlib
from .base import BASE_DIR


SETTINGS_MODULE = os.environ.get('ENVIRONMENT', 'local')

setting_module = importlib.import_module(f'core.settings.{SETTINGS_MODULE}')
setting_class = setting_module.Settings

settings = setting_class()