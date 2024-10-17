import inspect
from collections.abc import Callable
from typing import Any, Optional, Union

from fastapi import Depends


class Route:
    def __init__(
        self,
        path: str,
        endpoint: Union[Callable, type],
        tags: Optional[list[str]] = None,
        dependencies: Optional[list[Depends]] = None,
        responses: Optional[dict[Union[int, str], dict[str, Any]]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
        response_model: Optional[Any] = None,
        response_model_include: Optional[Union[dict[str, Any], list[str]]] = None,
        response_model_exclude: Optional[Union[dict[str, Any], list[str]]] = None,
        response_model_by_alias: bool = True,
        status_code: Optional[int] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        self.path = path
        self.endpoint = endpoint
        self.tags = tags
        self.dependencies = dependencies
        self.responses = responses
        self.summary = summary
        self.description = description
        self.deprecated = deprecated
        self.operation_id = operation_id
        self.response_model = response_model
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.status_code = status_code
        self.kwargs = kwargs
        self.name = name

    def get_route(self, path, endpoint, methods, name=""):
        return {
            "path": path,
            "endpoint": endpoint,
            "methods": methods,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "responses": self.responses,
            "summary": self.summary,
            "description": self.description,
            "deprecated": self.deprecated,
            "operation_id": self.operation_id,
            "response_model": self.response_model,
            "response_model_include": self.response_model_include,
            "response_model_exclude": self.response_model_exclude,
            "response_model_by_alias": self.response_model_by_alias,
            "status_code": self.status_code,
            "name": name,
            **self.kwargs,
        }

    def get(self):
        routes = []
        if inspect.isfunction(self.endpoint):
            # Handle function-based view
            route = self.get_route(
                self.path, self.endpoint, self.kwargs.get("methods", ["GET"]), name=self.endpoint.__name__
            )
            routes.append(route)
        else:
            # Handle class-based view
            endpoint = self.endpoint()
            if not self.name:
                chars = []
                for char in self.endpoint.__name__:
                    if char.isupper() and chars:  # Add underscore before uppercase letters
                        chars.append("_")
                    chars.append(char.lower())  # Convert to lowercase and add to the list
                self.name = "".join(chars)
            for route_obj in endpoint.get_routes():
                route = self.get_route(
                    self.path, **route_obj, name=f'{self.name}__{route_obj.get("endpoint").__name__}'
                )
                routes.append(route)

        return routes
