from core.admin import admin
from core.easy_router.app_config import AppConfig
from src.features.account.admin import UserAdminView


class AccountAppConfig(AppConfig):
    name = "account"
    ADMINS = [UserAdminView]

    def ready(self, **kwargs):
        for admin_view in self.ADMINS:
            admin.add_view(admin_view)


app = AccountAppConfig()
