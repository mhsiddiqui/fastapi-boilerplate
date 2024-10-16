from abc import ABC
from typing import Any

from fastapi import APIRouter


class AppConfig(ABC):
    def __init__(
        self,
        app_name: str,
        base_url: str = None,
        tags: list[str] = None,
        admins: list[Any] = None,
        router_kwargs=None
    ):
        self.app_name = app_name
        self.base_url = base_url
        self.tags = tags or []
        self.admins = admins or []
        self.router_kwargs = router_kwargs or {}

    def get_app_router(self):
        return APIRouter(tags=self.tags, prefix=self.base_url, **self.router_kwargs)

    def initialize_admin(self, admin):
        for admin_view in self.admins:
            admin.add_view(admin_view)

    def initialize_router(self, routes):

        app_router = self.get_app_router()

        for route_obj in routes:
            route_list = route_obj.get()
            for route in route_list:
                app_router.add_api_route(**route)

        return app_router
