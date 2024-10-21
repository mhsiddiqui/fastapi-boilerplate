from starlette_admin.contrib.sqla import ModelView

from core.admin import admin

from .models import User

UserAdminView = ModelView(User)

admin.add_view(UserAdminView)
