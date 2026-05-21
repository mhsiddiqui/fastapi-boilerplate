from starlette_admin.contrib.sqla import ModelView

from src.models.user import User


class UserView(ModelView):
    """User admin view.

    Password is intentionally not exposed (no view/edit). User creation is
    disabled here — use ``python manage.py create_superuser`` or the public
    registration endpoint instead, so the bcrypt hash path is the single
    source of truth.
    """

    can_create = False
    fields = [
        User.id,
        User.email,
        User.username,
        User.name,
        User.is_active,
        User.is_superuser,
        User.created,
        User.modified,
    ]
    exclude_fields_from_list = [User.id, User.modified]
    exclude_fields_from_edit = [User.id, User.created, User.modified]
    searchable_fields = [User.email, User.username, User.name]
    sortable_fields = [User.email, User.username, User.created, User.modified]
