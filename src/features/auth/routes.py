from core.easy_router.route import Route

from .api import login_for_access_token, logout, refresh_access_token

routes = [
    Route(path="/login/", endpoint=login_for_access_token, methods=["POST"]),
    Route(path="/refresh/", endpoint=refresh_access_token, methods=["POST"]),
    Route(path="/logout/", endpoint=logout, methods=["POST"]),
]
