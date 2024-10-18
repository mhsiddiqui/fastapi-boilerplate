from abc import ABC
from typing import Any

from fastapi import APIRouter

from core.easy_router.route import Route


class AppConfig(ABC):
    name: str
    base_url: str = None
    router_kwargs: dict = {}
    tags: list[str] = []

    def init(self, routes: list[Route] = None, **kwargs: Any):
        router = self.initialize_router(routes or [])
        self.ready(**kwargs)
        return router

    def get_app_router(self):
        if self.base_url:
            return APIRouter(tags=self.tags, prefix=self.base_url, **self.router_kwargs)

    def initialize_router(self, routes):
        app_router = self.get_app_router()
        for route_obj in routes:
            route_list = route_obj.get()
            for route in route_list:
                app_router.add_api_route(**route)
        return app_router

    def ready(self, **kwargs):
        pass
