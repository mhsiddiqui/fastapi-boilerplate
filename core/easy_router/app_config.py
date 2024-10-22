from abc import ABC
from typing import Any


class AppConfig(ABC):
    name: str

    def init(self, **kwargs: Any):
        self.ready(**kwargs)

    def ready(self, **kwargs):
        pass
