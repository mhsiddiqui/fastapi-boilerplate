import importlib
from typing import Any

from fastapi import APIRouter, FastAPI


class InstalledAppsInitializer:
    def __init__(
        self, app: FastAPI, router: APIRouter, package_name: str, installed_apps: list[str] = None, **kwargs: Any
    ):
        self.app = app
        self.package_name = package_name
        self.base_router = router
        self.installed_apps = installed_apps or []
        self.kwargs = kwargs

    def initialize(self):
        for app_name in self.installed_apps:
            app_module = importlib.import_module(f"{self.package_name}.{app_name}.app")
            installed_app = getattr(app_module, "app", None)
            if installed_app:
                routes_module = importlib.import_module(f"{self.package_name}.{app_name}.routes")
                if routes_module:
                    app_router = installed_app.init(routes=getattr(routes_module, "routes", []), **self.kwargs)
                    self.base_router.include_router(app_router)
