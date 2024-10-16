from .api import write_user, CurrentUserView
from core.easy_router.route import Route

routes = [
    Route(path="/users/", endpoint=write_user, methods=["POST"], status_code=201),
    Route(path="/users/me/", endpoint=CurrentUserView),
]