from abc import ABC, abstractmethod

from fastapi import Request, Response
from typing import Any


class BaseView(ABC):
    METHODS_MAP = {
        'get': ['GET'],
        'post': ['POST'],
        'put': ['PUT'],
        'patch': ['PATCH'],
        'delete': ['DELETE']
    }

    def get_routes(self):
        routes = []
        for method, mapping in self.METHODS_MAP.items():
            if hasattr(self, method):
                routes.append({'endpoint': getattr(self, method), 'methods': mapping})
        return routes
