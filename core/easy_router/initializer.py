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
