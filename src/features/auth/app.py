from core.easy_router.app_config import AppConfig


class AuthAppConfig(AppConfig):
    name = "auth"
    base_url = "/auth"
    tags = ["Authentication"]


app = AuthAppConfig()
