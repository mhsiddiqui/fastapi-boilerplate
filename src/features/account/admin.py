from starlette_admin.contrib.sqla import ModelView

from .models import User

UserAdminView = ModelView(User)
