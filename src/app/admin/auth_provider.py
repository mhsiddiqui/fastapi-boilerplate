import json

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from ..core.db.database import local_session
from ..core.security import authenticate_user


class UsernameAndPasswordProvider(AuthProvider):
    """
    This is only for demo purpose, it's not a better
    way to save and validate user credentials
    """

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 3:
            """Form data validation"""
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )

        if username and password:
            """Save `username` in session"""
            user = await authenticate_user(username, password, db=local_session())
            if user:
                request.session.update({'user': json.dumps(user, default=str)})
            else:
                raise LoginFailed("Invalid username or password")
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        if request.session.get('user'):
            request.state.user = request.session['user']
            return True
        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user = json.loads(request.state.user)  # Retrieve current user
        # Update app title according to current_user
        custom_app_title = "Hello, " + user["name"] + "!"
        # Update logo url according to current_user
        custom_logo_url = None
        if user.get("company_logo_url", None):
            custom_logo_url = request.url_for("static", path=user["company_logo_url"])
        return AdminConfig(
            app_title=custom_app_title,
            logo_url=custom_logo_url,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = json.loads(request.state.user)  # Retrieve current user
        photo_url = None
        if user.get("avatar") is not None:
            photo_url = request.url_for("static", path=user["avatar"])
        return AdminUser(username=user["name"])

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return RedirectResponse('/admin/login')