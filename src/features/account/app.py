from core.easy_router.app_config import AppConfig
from src.features.account.admin import UserAdminView

TAGS = ["Account"]
APP_NAME = 'account'
BASE_URL = '/account'
ADMINS = [
    UserAdminView
]

app = AppConfig(
    app_name=APP_NAME,
    tags=TAGS,
    base_url=BASE_URL,
    admins=ADMINS
)
