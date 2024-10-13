from .user import UserAdminView
from .auth_provider import UsernameAndPasswordProvider


def initialize_admin(admin):
    admin.add_view(UserAdminView)