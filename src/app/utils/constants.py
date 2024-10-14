from fastapi_babel.core import lazy_gettext as _


class Constants(object):
    pass

class Messages(object):
    USER = _('User')
    EMAIL_ALREADY_EXISTS = _("Email is already registered")
    NOT_AUTHENTICATED = _("User not authenticated")
    USERNAME_ALREADY_EXISTS = _("Username not available")
    OBJECT_NOT_FOUND = _("{object} not found")