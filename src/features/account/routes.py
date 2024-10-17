from core.easy_router.route import Route

from .api import CurrentUserView, write_user

routes = [
    Route(path="/users/", endpoint=write_user, methods=["POST"], status_code=201),
    Route(path="/users/me/", endpoint=CurrentUserView),
]
