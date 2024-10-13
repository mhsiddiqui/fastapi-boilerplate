from starlette_admin.contrib.sqla import ModelView
from ..models.user import User

UserAdminView = ModelView(User)
