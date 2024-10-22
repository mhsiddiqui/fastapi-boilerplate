import importlib
from typing import Any

from fastapi import APIRouter, FastAPI


class RoutesInitializer:
    def __init__(self, app: FastAPI, package: str, prefix: str = "", tags: list[str] = None, **kwargs: Any):
        self.app = app
        self.package = package
        self.prefix = prefix
        self.tags = tags
        self.kwargs = kwargs

    def initialize(self):
        router = APIRouter(prefix=self.prefix, tags=self.tags, **self.kwargs)
        route_module = importlib.import_module(self.package)
        if route_module:
            routes = getattr(route_module, "routes", [])
            for route_obj in routes:
                route_obj.add(router)
        self.app.include_router(router)


class AppsInitializer:
    def __init__(self, app: FastAPI, package: str, installed_apps: list[str], **kwargs: Any):
        self.app = app
        self.package = package
        self.installed_apps = installed_apps
        self.kwargs = kwargs

    def get_app_config(self, app):
        try:
            return importlib.import_module(f"{self.package}.{app}.app")
        except ModuleNotFoundError:
            return None

    def initialize(self):
        for app_name in self.installed_apps:
            app_module = self.get_app_config(app_name)
            if app_module:
                installed_app = getattr(app_module, "app", None)
                if installed_app:
                    installed_app.init(**self.kwargs)
