from fastcrud import FastCRUD

from ..account.models import User
from .schemas import UserCreateInternal, UserDelete, UserUpdate

CRUDUser = FastCRUD[User, UserCreateInternal, UserUpdate, UserUpdate, UserDelete]
crud_users = CRUDUser(User)
