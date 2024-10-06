from .user import UserAdminView
from ..core.db.database import admin
from .auth_provider import UsernameAndPasswordProvider


def initialize_admin(admin):
    admin.add_view(UserAdminView)