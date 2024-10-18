from core.easy_router.app_config import AppConfig
from src.features.account.admin import UserAdminView


class AccountAppConfig(AppConfig):
    name = "account"
    base_url = "/account"
    tags = ["Account"]
    ADMINS = [UserAdminView]

    def ready(self, **kwargs):
        admin = kwargs.get("admin")
        if admin:
            for admin_view in self.ADMINS:
                admin.add_view(admin_view)


app = AccountAppConfig()
