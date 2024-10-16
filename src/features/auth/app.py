from core.easy_router.app_config import AppConfig

TAGS = ["Authentication"]
APP_NAME = 'auth'
BASE_URL = '/auth'
ADMINS = []

app = AppConfig(
    app_name=APP_NAME,
    tags=TAGS,
    base_url=BASE_URL
)
