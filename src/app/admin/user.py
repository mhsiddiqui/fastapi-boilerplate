from starlette_admin.contrib.sqla import ModelView

# import bcrypt
# from fastadmin import SqlAlchemyModelAdmin, register
# from sqlalchemy import select
#
# from ..core.db.database import async_get_db, local_session
# from ..core.security import authenticate_user
from ..models.user import User
#
#
# @register(User, sqlalchemy_sessionmaker=local_session)
# class UserAdmin(SqlAlchemyModelAdmin):
#     exclude = ("hashed_password",)
#     list_display = ("id", "username", "is_superuser")
#     list_display_links = ("id", "username")
#     list_filter = ("id", "username", "is_superuser",)
#     search_fields = ("username",)
#
#     async def authenticate(self, username, password):
#         sessionmaker = self.get_sessionmaker()
#         # user = await authenticate_user(username, password, db=sessionmaker())
#         # if not user:
#         #     return None
#         # return user.get('id')
#         async with sessionmaker() as session:
#             query = select(User).filter_by(username=username, is_superuser=True)
#             result = await session.scalars(query)
#             user = result.first()
#             if not user:
#                 return None
#             if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
#                 return None
#             return user.id

UserAdminView = ModelView(User)